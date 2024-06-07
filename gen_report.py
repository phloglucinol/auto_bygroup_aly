from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth  # Import stringWidth
from PIL import Image, ImageFilter
import os  # To extract filenames from paths
from textwrap import wrap
from get_files_list import Bygroup_ABFE_files_getter

def gen_short_caption(files_list, file_type):
    for i in files_list:
        path_list = i.strip().split('/')
        side = path_list[-5]
        thermo_name = path_list[-4]
        images_name[i] = f'{side}_{thermo_name}_{file_type}'

ts = Bygroup_ABFE_files_getter(root_path=os.getcwd())
images = ts.get_timeseries_png_files()

images_name = {}
for count, i in enumerate(images):
    if count < 3:
        path_list = i.strip().split('/')
        images_name[i] = path_list[-1]
    else:
        path_list = i.strip().split('/')
        sys_name = path_list[-8]
        side= path_list[-6]
        thermo_name = path_list[-5]
        images_name[i] = f'{sys_name}_{side}_{thermo_name}'

reweighting_png_files = ts.get_reweighting_png_files() 
for i in reweighting_png_files:
    path_list = i.strip().split('/')
    side = path_list[-5]
    thermo_name = path_list[-4]
    if path_list[-1].startswith('dG_diff'):
        images_name[i] = f'{side}_{thermo_name}_dG_diff'
    else:
        images_name[i] = f'{side}_{thermo_name}_dG_percentage_diff'
images.extend(reweighting_png_files)

dGdl_png_files = ts.get_dGdl_png_files()
for i in dGdl_png_files:
    path_list = i.strip().split('/')
    side = path_list[-5]
    thermo_name = path_list[-4]
    images_name[i] = f'{side}_{thermo_name}_dG_dl'
images.extend(dGdl_png_files)

simu_time_png_files = ts.get_simu_time_png_files()
for i in simu_time_png_files:
    path_list = i.strip().split('/')
    sys_name = path_list[-2]
    images_name[i] = f'{sys_name}_thermoprocess_time'
images.extend(simu_time_png_files)

# images = [images[1]]

# print(images)
# print('---')
width, height = 9600, 13576
# Initialize the canvas
c = canvas.Canvas(f"{os.path.basename(os.getcwd())}_report.pdf", pagesize=(width, height))
# print(width, height)

# scaling_factor = 300 / 72  

# Configuration for layout
images_per_row = 2 
rows_per_page = 3 
x_margin = 50 * 16
y_margin = 50 * 16
inter_image_x = 10 * 16
inter_image_y = 30 * 16  # Increased to potentially accommodate larger captions

# Fixed font size
font_size = 10 * 16
c.setFont("Helvetica", font_size)

def calculate_caption_height(caption, max_width):
    wrap_width = int(max_width / (font_size * 0.6))
    wrapped_text = wrap(caption, width=wrap_width)
    return len(wrapped_text) * (font_size + 2)

def process_image(image_path, x, y, max_width, max_height):
    with Image.open(image_path) as img:
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            alpha = img.convert('RGBA').split()[-1]
            bg = Image.new("RGB", img.size, (255, 255, 255) + (255,))
            bg.paste(img, mask=alpha)
            img = bg
        # w_percent = (float(max_width) / float(img.size[0]))
        # h_size = int((float(img.size[1]) * float(w_percent)))
        # img = img.resize(
        #     (int(max_width * scaling_factor), int(max_height * scaling_factor)),
        #     Image.Resampling.LANCZOS
        # )
        # img.resize((int(max_width), h_size), Image.Resampling.LANCZOS)
        # print(img.size)
        # print(max_width, max_height)
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        # img = img.filter(ImageFilter.SHARPEN)
        # img.save('test.jpg', 'JPEG')
        img_reader = ImageReader(img)

        img_width, img_height = img.size
        image_x_center = x + (max_width - img_width) / 2
        c.drawImage(img_reader, image_x_center, y - img_height, width=img_width, height=img_height)
        # c.drawImage(img_reader, ((image_x_center)*inch/scale_factor), ((y - img_height)*inch/scale_factor), width=((img_width)*inch/scale_factor), height=((img_height)*inch/scale_factor))

        caption = images_name[image_path]  # Assuming you want to use the basename as the caption
        caption_width = stringWidth(caption, "Helvetica", font_size)
        caption_x_center = x + (max_width - caption_width) / 2  # Center the caption under the image
        caption_height = calculate_caption_height(caption, img_width)
        # Draw the caption centered under the image
        c.drawString(caption_x_center, y - img_height - caption_height, caption)

        return img_height + caption_height + 5

# usable_width = width - 2 * x_margin
# image_width = (usable_width - inter_image_x) / images_per_row
# image_height = (height - 2 * y_margin - (rows_per_page - 1) * inter_image_y) / rows_per_page

# x_position = x_margin
# y_position = height - y_margin
# for i, image_path in enumerate(images):
#     used_height = process_image(image_path, x_position, y_position, image_width, image_height)
#     if (i + 1) % images_per_row == 0:
#         x_position = x_margin
#         y_position -= (used_height + inter_image_y)
#     else:
#         x_position += (image_width + inter_image_x)
#     if (i + 1) % (images_per_row * rows_per_page) == 0:
#         c.showPage()
#         x_position = x_margin
#         y_position = height - y_margin
#         c.setFont("Helvetica", font_size)

# c.save()

usable_width = width - 2 * x_margin
# Since the special image will occupy a whole row, its width can be the entire usable width.
special_image_width = usable_width
image_width = (usable_width - inter_image_x) / images_per_row
image_height = (height - 2 * y_margin - (rows_per_page - 1) * inter_image_y) / rows_per_page

x_position = x_margin
y_position = height - y_margin

for i, image_path in enumerate(images):
    if image_path.endswith("thermoprocess_time.png"):
        # Check if the current position is not the start of a new page to avoid blank pages
        if x_position != x_margin or y_position != height - y_margin:
            c.showPage()
            x_position = x_margin
            y_position = height - y_margin
            c.setFont("Helvetica", font_size)
        
        # Process the special image to occupy the full width and reset positions
        used_height = process_image(image_path, x_position, y_position, special_image_width, image_height)
        c.showPage()  # Start a new page after the special image
        x_position = x_margin
        y_position = height - y_margin
        c.setFont("Helvetica", font_size)
        continue

    # Continue with the original logic for regular images
    used_height = process_image(image_path, x_position, y_position, image_width, image_height)
    if (i + 1) % images_per_row == 0:
        x_position = x_margin
        y_position -= (used_height + inter_image_y)
    else:
        x_position += (image_width + inter_image_x)
    
    # Check if a new page is needed
    if (i + 1) % (images_per_row * rows_per_page) == 0 or y_position < used_height:
        c.showPage()
        x_position = x_margin
        y_position = height - y_margin
        c.setFont("Helvetica", font_size)

c.save()