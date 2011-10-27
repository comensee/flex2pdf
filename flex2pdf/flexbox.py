#encoding: utf-8

from collections import defaultdict

from formdesigner.lib.draw import *


def get_image_dimension(box_height, image):
    h = image.size[0] / box_height * 0.8
    w = image.size[1] / box_height * 0.8
    return w,h


def generate_box(doc, struct):
    hauteur = int()
    for child in struct.childs:
        if child.css_class is not  'box':
            if child.height + child.y > 841:
                doc.showPage()
                page_w, page_h = A4
                child.flow(child.x,15,page_w-30)
            generate_box(doc, child)
        else:
            #doc.rect(child.x, child.y, child.width, child.height, 1, 0) if child.x else None
            if child.type=="text":
                draw_input = DrawText(doc, child)
                draw_input.make_input()
            if child.type=="field":
                draw_input = DrawField(doc, child)
                draw_input.make_input()
            else:
                draw_input = DrawGeo(doc, child)
                draw_input.make_input()

def last_box(flex):
    if len(flex.childs) > 0:
        if flex.childs[-1].css_class != "box":
            last_box(flex.childs[-1])
        else:
            print flex.childs[-1]
            return "eeeeeeeeeeeee"


class Flex(object):

    def __init__(self, flex, childs):
        self.flex = flex
        self.childs = childs
        self.height = int()
        
        
    def __html__(self):
        content = '\n'.join( '\n'.join('\t'+line for line in child.__html__().splitlines()) for child in self.childs )
        return "<div class='{css_class} flex{flex}'>\n{content}\n</div>".format(css_class=self.css_class, content=content, flex=self.flex)







class HFlex(Flex):
    css_class = 'hflex'
    width = int()
    x = int()
    y = int()


    def get_width(self):
        for child in self.childs:
            width = int()
            if len(child.childs) > 0:
                if child.css_class is not 'box':
                    width += self.width * (child.flex / sum([child.flex for child in self.childs]))
        return width

    def get_child_width(self, child, width):
        child_width = width * child.flex / sum([child_element.flex for child_element in self.childs])
        return child_width

    def flow(self, x, y, width, level = 0):
        self.x = x
        self.y = y
        self.level = level
        self.width = width
        self.height = int()
        self.height = max([child.flow(self.x if idx == 0 else
                            self.childs[idx-1].x + self.get_child_width(self.childs[idx-1],
                            self.width),self.y,
                            self.get_child_width(child, self.width),level +1) for idx,child in enumerate(self.childs)])

        return self.height

class VFlex(Flex):
    css_class = 'vflex'
    width = int()
    x = int()
    y = int()

    def flow(self, x, y, width, level = 0):
        self.x = x
        self.y = y
        self.level = level
        self.width = width
        self.height = int()
        
        for idx, child in enumerate(self.childs):
            self.height += child.flow(self.x, (self.childs[idx-1].height if child !=self.childs[0] else self.y) + (self.childs[idx-1].y if child !=self.childs[0] else 0), self.width,level +1) if self.height < 800 else 0
        childs_in = [child for child in self.childs if child.height != 0]
        childs_out = [child for child in self.childs if child.height == 0]
        if len(childs_in[-1].childs) > 0:
            try:
                print childs_in[-1].childs[-1].__dict__
                if childs_in[-1].childs[-1].type != "field":
                    childs_out.insert(0, childs_in[-1])
                    del childs_in[-1]
            except:pass
        if self.level == 0 :
            return self.height, childs_in, childs_out
        else:
            return self.height

class Box(object):
    
    def __init__(self, kwargs):
        for (attr,data) in kwargs.items():
            setattr(self, attr, data) if attr !='flex' else setattr(self, attr, int(data))
        self.height = basic_height + 15 if self.type =='field' and self.label_class=="label-top" else basic_height
        if self.type=='text':
            if self.text_class == u"text-xlarge":
                self.height = 60
            elif self.text_class == u"text-large":
                self.height = 45
            elif self.text_class == u"text-normal":
                self.height = 40
            elif self.text_class == u"text-small":
                self.height = basic_height
        
        if self.photo_size_class is not None and self.flex==0:
            self.flex = 1
        if self.photo_size_class =='photo-size-small':
            self.height = 60
        if self.photo_size_class =='photo-size-normal':
            self.height = 90
        if self.photo_size_class =='photo-size-large':
            self.height = 120
        if self.photo_size_class =='photo-size-xlarge':
            self.height = 240
        self.css_class = 'box'
        self.childs = []
        
    def __html__(self):
        return "<div class='box v{height}'>{text}</div>".format(**self.__dict__)


    def flow(self, x, y, width, level = 0):
        self.x = x
        self.y = y
        self.level = level
        self.width = width
        return self.height
        #largeur_box = grande_largeur * (valeur_flex / nb_box)



