
#encoding: utf-8

from reportlab.lib.pagesizes import A4
from formdesigner.model import *
#from formdesigner.lib.form_struct import form
from formdesigner.lib.flexbox import *
field_map = dict((field['id'],field) for field in form['items'])
field_section = dict((field['id'],field) for field in form['items'])
import os.path


def print_field(field, pfx):
    keys = field.keys()
    keys.remove('id')
    keys.sort()
    for key in keys:
        print pfx,key,field[key]
    
def list_box_snippet(id,base=True):
    list_box = []
    snippet = form['snippets'][id]
    for child in snippet:
        if child.type =='Box':
            list_box.extend(child)
        else:
            list_box_snippet(id,)

def dispatch_params(node, config={}, is_child=True):
    #print node['config']['list']
    if is_child is False:
        config = node.get('config')
        
    for child in node['childs']:
        if child['#type_name']!='Box':
            dispatch_params(child, config)
        else:
            box =  field_map[child['id']]
            if box['type']=="image":
                box['ref'] = config['list']
                
                



def scan_tree(root, level=0):
    pfx="\t"*level
    for node in root:
        node_type=node['#type_name']
        obj_type = {'HFlex':HFlex, 'VFlex':VFlex, 'Box':Box,'Section':VFlex}[node_type]
        node['level'] = level
        if  node_type == 'Box':
            box = field_map[node['id']]
            box['value'] = datas.get(node['id'])
            box['bolder'] = box.get('bolder')
            box['needed'] = box.get('needed')
            box['photo_size_class'] = box.get('photo_size_class')
            if box['type']=='image':
                image_list = db[box['ref']]
                #image_test = DesignImage(db['38450255873719c6f5243d16e628c270'])
                image_test = DesignImage(db[image_list['content'][0]['img_ref']])
                box['label'] = os.path.join(os.getcwdu(), 'formdesigner','public','user_img',image_test.get_base_path('s'))
            obj = obj_type(box)
        elif node_type=="Section":
            dispatch_params(node, node.get('config'), False)
            obj = obj_type(node['flex'],[scan_tree([node],level+1) for node in node['childs']])
        else:
            obj = obj_type(node['flex'],[scan_tree([node],level+1) for node in node['childs']])
    return obj

def separate_vflex(struct):
    page_w, page_h = A4
    list_element = []
    height_struct, childs_in, childs_out = struct.flow(15,15,page_w-30)
    list_element.append(VFlex(1, childs_in))
    if len(childs_out) > 0:
        new_flex = VFlex(1, childs_out)
        list_element.extend(separate_vflex(new_flex))
    return list_element
    
    