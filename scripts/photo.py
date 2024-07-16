import conf
import os
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

Image.MAX_IMAGE_PIXELS = 933120000

class Photo():
    def __init__(self, path):
        self.path = path
        self.min_path = ''
        try:
            self.pil_image = Image.open(self.path).convert('RGBA')
        except (OSError, UnidentifiedImageError) as e:
            print(f"Error opening image {self.path}: {e}")
            self.pil_image = None
            return

        self.width, self.height = self.pil_image.size
        self.size = self.pil_image.size

        min_file = self.path.stem + '.min' + self.path.suffix
        self.min_path = self.path.with_name(min_file)

    @property
    def is_min(self):
        return self.path.match('*.min.jpg')

    @property
    def has_min(self):
        return self.min_path.exists()

    def format(self):
        if self.pil_image is None:
            return None

        if self.is_min:
            return None

        if not self.has_min:
            if conf.SIGN_ORIGINAL:
                signed_image = self.mark_image(self.pil_image, conf.fontsize)
                self.save_image(signed_image, self.path)

            # resize
            ratio = float(conf.MIN_WIDTH) / self.size[0]
            new_image_size = tuple([int(x * ratio) for x in self.size])

            if conf.SIGN_THUMBNAIL:
                if not conf.SIGN_ORIGINAL:
                    signed_image = self.mark_image(self.pil_image, conf.fontsize)
                signed_image.thumbnail(new_image_size, Image.LANCZOS)
                self.save_image(signed_image, self.min_path)
            else:
                min_image = self.pil_image.copy()
                min_image.thumbnail(new_image_size, Image.LANCZOS)
                self.save_image(min_image, self.min_path)

        relative_path = str(self.path.relative_to(conf.DIR_PATH))

        # return basic info
        return {
            "type": 'photo',
            'width': self.size[0],
            'height': self.size[1],
            'path': './' + relative_path,
            'min_path': './' + str(self.min_path.relative_to(conf.DIR_PATH))
        }

    def save_image(self, img, path):
        if conf.DEBUG:
            img.show()
        else:
            img.save(path, 'PNG')

    def mark_image(self, img, fontsize):
        width, height = img.size
        transparent_image = Image.new('RGBA', img.size, (255, 255, 255, 0))

        base_font_path = '/Users/bemeadows/Documents/GitHub/horcrux/assets/font/Eczar-Medium.ttf'
        if conf.fontfamily:
            font_path = os.path.join('/Users/bemeadows/Documents/GitHub/horcrux/assets/font/', f'{conf.fontfamily}')
        else:
            font_path = base_font_path

        print(f"Trying to load font from: {font_path}")

        try:
            font = ImageFont.truetype(font_path, fontsize)
        except OSError as e:
            print(f"Error loading font: {e}")
            try:
                font = ImageFont.load_default()
            except:
                print("Failed to load default font. Returning original image.")
                return img

        draw = ImageDraw.Draw(transparent_image)

        # Use getbbox instead of getsize
        bbox = font.getbbox(conf.copyright)
        t_w = bbox[2] - bbox[0]  # right - left
        t_h = bbox[3] - bbox[1]  # bottom - top

        x = (width - t_w) / 2
        y = height - 2 * t_h

        draw.text((x, y), conf.copyright, font=font, fill=(255, 255, 255, 125))
        transparent_image = transparent_image.rotate(conf.watermark_rotate)
        signed_image = Image.alpha_composite(img, transparent_image)
        return signed_image
