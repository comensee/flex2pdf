# encoding: utf-8
import os

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from reportlab.lib.units import inch

from reportlab.lib.pagesizes import A4

from StringIO import StringIO

from flex2pdf import draw
from flex2pdf import flexbox



from formdesigner.model import *
field_map = dict((field['id'],field) for field in form['items'])
field_section = dict((field['id'],field) for field in form['items'])

class Flex2Pdf(object):
	
	
	
    def __init__(self, filename=None,font='Helvetica', base_size=10):
        self.filename = filename
        self.font = font
        self.base_size = base_size
        self.obj = None
        self.list_element = []
        
        
        
        
    def dispatch_params(self, node, config={}, is_child=True):
        if is_child is False:
            config = node.get('config')
        for child in node['childs']:
            if child['#type_name']!='Box':
                self.dispatch_params(child, config)
            else:
                box =  field_map[child['id']]
                if box['type']=="image":
                    box['ref'] = config['list']

    def separate_vflex(self, struct):
        page_w, page_h = A4
        height_struct, childs_in, childs_out = struct.flow(15,15,page_w-30)
        self.list_element.append(flexbox.VFlex(1, childs_in))
        if len(childs_out) > 0:
            new_flex = flexbox.VFlex(1, childs_out)
            self.list_element.extend(self.separate_vflex(new_flex))
        return self.list_element


    def scan(self, root, level=0):
        for node in root:
            node_type=node['#type_name']
            obj_type = {'HFlex':flexbox.HFlex, 'VFlex':flexbox.VFlex, 'Box':flexbox.Box,'Section':flexbox.VFlex}[node_type]
            node['level'] = level
            if  node_type == 'Box':
                box = field_map[node['id']]
                box['value'] = datas.get(node['id'])
                box['bolder'] = box.get('bolder')
                box['needed'] = box.get('needed')
                box['photo_size_class'] = box.get('photo_size_class')
                if box['type']=='image':
                    image_list = db[box['ref']]
                    image_test = draw.DesignImage(db[image_list['content'][0]['img_ref']])
                    box['label'] = os.path.join(os.getcwdu(), 'formdesigner','public','user_img',image_test.get_base_path('s'))
                obj = obj_type(box)
            elif node_type=="Section":
                self.dispatch_params(node, node.get('config'), False)
                obj = obj_type(node['flex'],[self.scan([node],level+1) for node in node['childs']])
            else:
                obj = obj_type(node['flex'],[self.scan([node],level+1) for node in node['childs']])
                
        return obj
    
    
    def get_datas():
        return ''

        
    def generate(self, structure):
        self.buf = StringIO()
        self.doc = canvas.Canvas(self.buf, bottomup = 0)
        
        self.doc.setFont(self.font, self.base_size)
        for struct in self.separate_vflex(structure):
            self.doc.setLineWidth(0.12)
            flexbox.generate_box(self.doc, struct)
            self.doc.showPage()
        self.doc.save()
        self.buf.seek(0)

        
        
    
    def readx(self):
        return self.buf.read()
        
