from PIL import Image
import piltextbox


def render_text(text, font_size=25, size=(300, 96)):
    """Use PIL to render text as an image in 90 degree rotation  (clockwise)"""

    tb1 = piltextbox.TextBox(
        size,
        typeface="arial.ttf",
        font_size=font_size,
        paragraph_indent=0,
        new_line_indent=6,
        spacing=4,
        margins=(0, 35, 0, 0),
    )
    tb1.write_line(text)
    image = tb1.render()
    return image.transpose(Image.ROTATE_270)
