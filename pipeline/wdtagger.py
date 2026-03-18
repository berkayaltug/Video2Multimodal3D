import gradio as gr
import huggingface_hub
import numpy as np
import pandas as pd
from PIL import Image

try:
    import gradio as gr
except Exception:
    class _GradioCompat:
        @staticmethod
        def update(**kwargs):
            return kwargs

    gr = _GradioCompat()

# Dataset v3 series of models:
SWINV2_MODEL_DSV3_REPO = "SmilingWolf/wd-swinv2-tagger-v3"
CONV_MODEL_DSV3_REPO = "SmilingWolf/wd-convnext-tagger-v3"
VIT_MODEL_DSV3_REPO = "SmilingWolf/wd-vit-tagger-v3"
VIT_LARGE_MODEL_DSV3_REPO = "SmilingWolf/wd-vit-large-tagger-v3"
EVA02_LARGE_MODEL_DSV3_REPO = "SmilingWolf/wd-eva02-large-tagger-v3"

# Dataset v2 series of models:
MOAT_MODEL_DSV2_REPO = "SmilingWolf/wd-v1-4-moat-tagger-v2"
SWIN_MODEL_DSV2_REPO = "SmilingWolf/wd-v1-4-swinv2-tagger-v2"
CONV_MODEL_DSV2_REPO = "SmilingWolf/wd-v1-4-convnext-tagger-v2"
CONV2_MODEL_DSV2_REPO = "SmilingWolf/wd-v1-4-convnextv2-tagger-v2"
VIT_MODEL_DSV2_REPO = "SmilingWolf/wd-v1-4-vit-tagger-v2"

# deepghs models:
SWINV2_MODEL_DGHS_IDOLSANKAKU_REPO = "deepghs/idolsankaku-swinv2-tagger-v1"
EVA02_LARGE_MODEL_DGHS_IDOLSANKAKU_REPO = "deepghs/idolsankaku-eva02-large-tagger-v1"

# Files to download from the repos
MODEL_FILENAME = "model.onnx"
LABEL_FILENAME = "selected_tags.csv"

# https://github.com/toriato/stable-diffusion-webui-wd14-tagger/blob/a9eacb1eff904552d3012babfa28b57e1d3e295c/tagger/ui.py#L368
kaomojis = [
    "0_0",
    "(o)_(o)",
    "+_+",
    "+_-",
    "._.",
    "<o>_<o>",
    "<|>_<|>",
    "=_=",
    ">_<",
    "3_3",
    "6_9",
    ">_o",
    "@_@",
    "^_^",
    "o_o",
    "u_u",
    "x_x",
    "|_|",
    "||_||",
]


def _people_tag(noun: str, minimum: int = 1, maximum: int = 5):
    return (
        [f"1{noun}"]
        + [f"{num}{noun}s" for num in range(minimum + 1, maximum + 1)]
        + [f"{maximum+1}+{noun}s"]
    )


PEOPLE_TAGS = (
    _people_tag("girl") + _people_tag("boy") + _people_tag("other") + ["no humans"]
)


RATING_MAP = {
    "general": "safe",
    "sensitive": "sensitive",
    "questionable": "nsfw",
    "explicit": "explicit, nsfw",
    "safe": "safe",
    "nsfw": "nsfw",
}
DANBOORU_TO_E621_RATING_MAP = {
    "safe": "rating_safe",
    "sensitive": "rating_safe",
    "nsfw": "rating_explicit",
    "explicit, nsfw": "rating_explicit",
    "explicit": "rating_explicit",
    "rating:safe": "rating_safe",
    "rating:general": "rating_safe",
    "rating:sensitive": "rating_safe",
    "rating:questionable, nsfw": "rating_explicit",
    "rating:explicit, nsfw": "rating_explicit",
}


def load_labels(dataframe) -> list[str]:
    name_series = dataframe["name"]
    name_series = name_series.map(
        lambda x: x.replace("_", " ") if x not in kaomojis else x
    )
    tag_names = name_series.tolist()

    rating_indexes = list(np.where(dataframe["category"] == 9)[0])
    general_indexes = list(np.where(dataframe["category"] == 0)[0])
    character_indexes = list(np.where(dataframe["category"] == 4)[0])
    return tag_names, rating_indexes, general_indexes, character_indexes


def mcut_threshold(probs):
    """
    Maximum Cut Thresholding (MCut)
    Largeron, C., Moulin, C., & Gery, M. (2012). MCut: A Thresholding Strategy
     for Multi-label Classification. In 11th International Symposium, IDA 2012
     (pp. 172-183).
    """
    sorted_probs = probs[probs.argsort()[::-1]]
    difs = sorted_probs[:-1] - sorted_probs[1:]
    t = difs.argmax()
    thresh = (sorted_probs[t] + sorted_probs[t + 1]) / 2
    return thresh


class Predictor:
    def __init__(self):
        self.model_target_size = None
        self.last_loaded_repo = None
        self._rt = None

    def _get_runtime(self):
        if self._rt is None:
            import onnxruntime as rt

            self._rt = rt
        return self._rt

    def download_model(self, model_repo):
        csv_path = huggingface_hub.hf_hub_download(
            model_repo,
            LABEL_FILENAME,
        )
        model_path = huggingface_hub.hf_hub_download(
            model_repo,
            MODEL_FILENAME,
        )
        return csv_path, model_path

    def load_model(self, model_repo):
        if model_repo == self.last_loaded_repo:
            return

        csv_path, model_path = self.download_model(model_repo)

        tags_df = pd.read_csv(csv_path)
        sep_tags = load_labels(tags_df)

        self.tag_names = sep_tags[0]
        self.rating_indexes = sep_tags[1]
        self.general_indexes = sep_tags[2]
        self.character_indexes = sep_tags[3]

        runtime = self._get_runtime()
        model = runtime.InferenceSession(model_path)
        _, height, width, _ = model.get_inputs()[0].shape
        self.model_target_size = height

        self.last_loaded_repo = model_repo
        self.model = model

    def prepare_image(self, image):
        target_size = self.model_target_size

        canvas = Image.new("RGBA", image.size, (255, 255, 255))
        canvas.alpha_composite(image)
        image = canvas.convert("RGB")

        # Pad image to square
        image_shape = image.size
        max_dim = max(image_shape)
        pad_left = (max_dim - image_shape[0]) // 2
        pad_top = (max_dim - image_shape[1]) // 2

        padded_image = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
        padded_image.paste(image, (pad_left, pad_top))

        # Resize
        if max_dim != target_size:
            padded_image = padded_image.resize(
                (target_size, target_size),
                Image.BICUBIC,
            )

        # Convert to numpy array
        image_array = np.asarray(padded_image, dtype=np.float32)

        # Convert PIL-native RGB to BGR
        image_array = image_array[:, :, ::-1]

        return np.expand_dims(image_array, axis=0)

    def predict(
        self,
        image,
        model_repo,
        general_thresh,
        general_mcut_enabled,
        character_thresh,
        character_mcut_enabled,
    ):
        self.load_model(model_repo)

        image = self.prepare_image(image)

        input_name = self.model.get_inputs()[0].name
        label_name = self.model.get_outputs()[0].name
        preds = self.model.run([label_name], {input_name: image})[0]

        labels = list(zip(self.tag_names, preds[0].astype(float)))

        # First 4 labels are actually ratings: pick one with argmax
        ratings_names = [labels[i] for i in self.rating_indexes]
        rating = dict(ratings_names)

        # Then we have general tags: pick any where prediction confidence > threshold
        general_names = [labels[i] for i in self.general_indexes]

        if general_mcut_enabled:
            general_probs = np.array([x[1] for x in general_names])
            general_thresh = mcut_threshold(general_probs)

        general_res = [x for x in general_names if x[1] > general_thresh]
        general_res = dict(general_res)

        # Everything else is characters: pick any where prediction confidence > threshold
        character_names = [labels[i] for i in self.character_indexes]

        if character_mcut_enabled:
            character_probs = np.array([x[1] for x in character_names])
            character_thresh = mcut_threshold(character_probs)
            character_thresh = max(0.15, character_thresh)

        character_res = [x for x in character_names if x[1] > character_thresh]
        character_res = dict(character_res)

        sorted_general_strings = sorted(
            general_res.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        sorted_general_strings = [x[0] for x in sorted_general_strings]
        sorted_general_strings = (
            ", ".join(sorted_general_strings).replace("(", "\(").replace(")", "\)")
        )

        return sorted_general_strings, rating, character_res, general_res


dropdown_list = [
    SWINV2_MODEL_DSV3_REPO,
    CONV_MODEL_DSV3_REPO,
    VIT_MODEL_DSV3_REPO,
    VIT_LARGE_MODEL_DSV3_REPO,
    EVA02_LARGE_MODEL_DSV3_REPO,
    MOAT_MODEL_DSV2_REPO,
    SWIN_MODEL_DSV2_REPO,
    CONV_MODEL_DSV2_REPO,
    CONV2_MODEL_DSV2_REPO,
    VIT_MODEL_DSV2_REPO,
    SWINV2_MODEL_DGHS_IDOLSANKAKU_REPO,
    EVA02_LARGE_MODEL_DGHS_IDOLSANKAKU_REPO,
]


def get_wdtagger_models():
    return dropdown_list


predictor = Predictor()


def to_list(s):
    return [x.strip() for x in s.split(",") if not s == ""]


def list_uniq(l):
    return sorted(set(l), key=l.index)


def load_dict_from_csv(filename):
    from pathlib import Path
    dict = {}
    if not Path(filename).exists(): return dict
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        print(f"Failed to open dictionary file: {filename}")
        return dict
    for line in lines:
        parts = line.strip().split(',')
        dict[parts[0]] = parts[1]
    return dict


anime_series_dict = load_dict_from_csv('character_series_dict.csv')


def character_list_to_series_list(character_list):
    output_series_tag = []
    series_tag = ""
    series_dict = anime_series_dict
    for tag in character_list:
        series_tag = series_dict.get(tag, "")
        if tag.endswith(")"):
            tags = tag.split("(")
            character_tag = "(".join(tags[:-1])
            if character_tag.endswith(" "):
                character_tag = character_tag[:-1]
            series_tag = tags[-1].replace(")", "")

    if series_tag:
        output_series_tag.append(series_tag)

    return output_series_tag


def postprocess_results(results: dict[str, float], res_rate: dict[str, float], res_char: dict[str, float],
                         general_threshold: float, character_threshold: float):
    results = {
        k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)
    }

    rating = res_rate
    character = {}
    general = {}

    character = {k: v for k, v in res_char.items() if v >= character_threshold}
    general = {k: v for k, v in results.items() if v >= general_threshold}

    return rating, character, general


def gen_prompt(rating: list[str], character: list[str], general: list[str]):
    people_tags: list[str] = []
    other_tags: list[str] = []
    rating_tag = RATING_MAP[rating[0]] if rating else []

    for tag in general:
        if tag in PEOPLE_TAGS:
            people_tags.append(tag)
        else:
            other_tags.append(tag)

    all_tags = people_tags + other_tags

    return ", ".join(all_tags)


def predict_tags(image: Image.Image, general_threshold: float = 0.3, character_threshold: float = 0.8,
                 input_tags: str = "", input_series: str = "", input_character: str = "", model_repo = VIT_LARGE_MODEL_DSV3_REPO):
    general_str, rating_res, character_res, general_res = predictor.predict(image.convert("RGBA"), model_repo, general_threshold, False, character_threshold, False)
    rating, character, general = postprocess_results(
        general_res, rating_res, character_res, general_threshold, character_threshold
    )
    prompt = gen_prompt(
        list(rating.keys()), list(character.keys()), list(general.keys())
    )
    output_series_tag = input_series
    output_series_list = character_list_to_series_list(character.keys())
    if output_series_list:
        output_series_tag = output_series_list[0]
    else:
        output_series_tag = input_series
    output_character_tag = ", ".join(list_uniq(to_list(input_character) + list(character.keys())))
    output_prompt = ", ".join(list_uniq(to_list(input_tags) + to_list(prompt)))
    return output_series_tag, output_character_tag, output_prompt, gr.update(interactive=True)


def predict_tags_wd_large(image: Image.Image, input_tags: str, algo: list[str], general_threshold: float = 0.3,
                     character_threshold: float = 0.8, input_series: str = "", input_character: str = "",
                     model_repo = VIT_LARGE_MODEL_DSV3_REPO):
    if not "Use Original WD Tagger" in algo:
        return input_series, input_character, input_tags, gr.update(interactive=True)
    return predict_tags(image, general_threshold, character_threshold, input_tags, input_series, input_character, model_repo)

