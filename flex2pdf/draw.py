# encoding: utf-8

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import *
from cStringIO import StringIO

try:
    import Image
except ImportError:
    from PIL import Image
    
import os

basic_height = 30
MARGIN = 12

class DesignImage(object):

    def __init__(self, kwargs):
        for (attr,data) in kwargs.items():
            setattr(self, attr, data) if attr !='flex' else setattr(self, attr, int(data))

    ext_map = {'JPEG':'jpg', 'PNG':'png'}

    def store_image(self, file, filename=None):
        p = ImageFile.Parser()

        data = file.read()
        p.feed(data)
        im = p.close()

        if im.format not in self.ext_map:
            raise Exception('Bad format')

        self.format = im.format
        self.width, self.height = im.size
        self.filename = filename

        # Save original
        path = self.get_path('o')
        base, _ = os.path.split(path)
        if not os.path.exists(base):
            os.makedirs(base)

        with open(path, 'wb') as out:
            out.write(data)

        # Now for two sizes

        for typ, factor in ( ('s', 320.0), ('l', 1024.0) ):
            if self.orientation=='p':
                factor /= self.height
            else:
                factor /= self.width

            new_size = (int(self.width*factor), int(self.height*factor))
            new_pic = im.resize(new_size, PIL_Image.ANTIALIAS)

            path = self.get_path(typ)
            new_pic.save(path, quality=90, optimize=True)
            new_pic = None


    @property
    def orientation(self):
        return 'p' if self.width < self.height else 'l'

    def get_base_path(self, type):
        ext = self.ext_map[self.format]
        return '{base}/{name}-{type}.{ext}'.format(base=self._id[:2], name=self._id, ext=ext, type=type)

    def get_path(self, type):
        return os.path.join('formdesigner', 'static', 'user_img', self.get_base_path(type))

    def get_url(self, type):
        return '/'.join(('/static', 'user_img', self.get_base_path(type)))







class Drawing(object):

    def __init__(self, document, x,y, width, height, label, input_type, layout = 'label-top', rotate=False, rounded=False):
        self.document = document
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.layout = layout #label-top / label-left  / in / none
        self.input_type = input_type # text(basic_height) / ellipsis (basic_height) 
        self.rounded = rounded
        self.rounded_angle = 4
        self.rotate = rotate


    @property
    def box_height(self):
        return self.height - 5

    @property
    def box_width(self):
        return self.width - 5 - MARGIN

    def render_need(self):
        self.document.setFillColor('#eeeeee')

    def clear_render(self):
        self.document.setFillColor(black)

        
class DrawField(Drawing):
    def __init__(self, doc, box, rotate=False, rounded=True):
        for key,val in box.__dict__.items():
            setattr(self, key, val)
        self.document = doc
        self.rounded = rounded
        self.rounded_angle = 4
        self.rotate = rotate
        
    def draw_label(self):
        self.document.setFont("Helvetica-Bold", 9) if self.bolder is not None else self.document.setFont("Helvetica", 9)
        if self.label_class == 'label-top':
            self.document.drawString(self.x + 10, self.y + 15,self.label)
        elif self.label_class == 'label-left':
            self.document.drawString(self.x + 12 , self.y + 25,self.label)
        elif self.label_class == 'label-inside':
            self.document.setFillColor(darkgray)
            self.document.setFont("Helvetica", 9)
            self.document.drawString(self.x  + 18 , self.y + 25,self.label)
            self.document.setFillColor(black)
        elif self.label_class == 'label-none':
            self.document.drawString(self.x  + 15 , self.y + 22,self.label)
        self.document.setFont("Helvetica", 9)

    def draw_value(self):
        self.document.setFontSize(12)
        if self.label_class == 'label-top':
            self.document.drawString(self.x + MARGIN + 10, self.y + 40,self.value)
        elif self.label_class == 'label-left':
            self.document.drawString(self.x  + MARGIN + self.document.stringWidth(self.label) + 12 , self.y + 25,self.value)
        elif self.label_class == 'label-inside':
            self.document.drawString(self.x  + 18 , self.y + 25,self.value)
        elif self.label_class == 'label-none':
            self.document.drawString(self.x  + 15 , self.y + 22,self.value)
        self.document.setFontSize(10)

    def draw_input(self, height = basic_height):
        if self.needed is not None:
            self.render_need()
        if self.label_class == 'label-top':
            self.document.roundRect(self.x  + MARGIN, self.y + 25, self.box_width, self.box_height - 15,self.rounded_angle if self.rounded else 0, 1, 1 if self.needed is not None else 0)
        elif self.label_class == 'label-left':
            self.document.roundRect(self.x  + MARGIN + self.document.stringWidth(self.label) + 5  if self.bolder is None else self.x  + MARGIN + self.document.stringWidth(self.label) + 12,
            self.y  + 10, self.box_width - self.document.stringWidth(self.label) - 5, self.box_height,self.rounded_angle if self.rounded else 0,1, 1 if self.needed is not None else 0)
        elif self.label_class == 'label-inside':
            self.document.roundRect(self.x + MARGIN, self.y +10, self.box_width, self.box_height,self.rounded_angle if self.rounded else 0,1, 1 if self.needed is not None else 0)
        if self.needed is not None:
            self.clear_render()
        if self.value is not None and self.label_class == "label-inside":
            self.draw_value()
        else:
            self.draw_label()
            if self.value is not None:
                self.draw_value()

        
    def make_input(self):
        self.draw_input(self.height)


        
class DrawText(Drawing):
    def __init__(self, doc, box):
        for key,val in box.__dict__.items():
            setattr(self, key, val)
        self.document = doc
        self.rounded = False
        
        
    def draw_input(self, height = basic_height):
        if self.back_class == "back-dark":
            self.document.setStrokeColor(white)
            self.document.setFillColor(darkgray)
            self.document.setStrokeColor(white)
        elif self.back_class == "back-light":
            self.document.setStrokeColor(white)
            self.document.setFillColor(lightgrey)
            self.document.setStrokeColor(white)
        elif self.back_class == "back-none":
            self.document.setStrokeColor(white)
            self.document.setFillColor(white)
        self.document.roundRect(self.x + MARGIN, self.y +10, self.box_width, self.box_height,self.rounded_angle if self.rounded else 0,1, 1)
        self.document.setFillColor(black)
        self.document.setStrokeColor(black)



    def draw_paragraph(self):

        x = self.x + MARGIN
        y = self.y +10
        if self.text_class == "text-xlarge":
            self.document.setFontSize(18)
            self.document.setFillColor(white)
            self.document.drawString(x  + 10 , y + 35,self.text)
            self.document.setFillColor(black)
        elif self.text_class == "text-large":
            self.document.setFontSize(12)
            self.document.drawString(x  + 10 , y + 25,self.text)
            self.document.setFillColor(black)
        elif self.text_class == "text-normal":
            self.document.setFontSize(10)
            self.document.drawString(x  + 10 , y + 15,self.text)
            self.document.setFillColor(black)
        elif self.text_class == "text-small":
            self.document.setFontSize(9)
            self.document.drawString(x  + 10 , y + 15,self.text)
            self.document.setFillColor(black)
        self.document.setFontSize(9)

    def make_input(self):
        self.draw_input()
        self.draw_paragraph()

class DrawGeo(Drawing):
    def __init__(self, doc, box, rotate=True):
        for key,val in box.__dict__.items():
            setattr(self, key, val)
        self.document = doc
        self.rounded = False
        self.rotate = rotate
        
    def draw_image(self):
        self.document.saveState()
        self.document.scale(1, -1)
        self.document.drawImage(self.label, self.x + 5,-(self.y + 7), self.width, -self.height,preserveAspectRatio=True, anchor='c', mask='auto')
        self.document.restoreState()


    def draw_ellipsis(self):
        self.draw_label()
        if self.layout == 'label-top':
            self.document.ellipse(self.x  + 12, self.y +13, self.x  + 21,self.y +20, stroke=1, fill=0)
        elif self.layout == 'label-left ':
            self.document.ellipse(self.x  + 12 + self.document.stringWidth(self.label), self.y +10, self.x  + 24 + self.document.stringWidth(self.label),self.y +22, stroke=1, fill=0)
        elif self.layout == 'label-inside':
            pass
        elif self.layout == 'label-none':
            pass


    def make_input(self):
        if self.type=='image':
            self.draw_image()
        elif self.type=='ellipsis':
            self.draw_ellipsis()