import unittest
import json
import os
import hashlib

from libs import actions, tools, contract, check, api, db


class TestPrototipo():
    conf = tools.read_config('nodes')
    pages = tools.read_fixtures('pages')
    url = conf[0]['url']
    pr_key = conf[0]['private_key']
    db1 = conf[0]['db']
    wait = tools.read_config('test')['wait_tx_status']

    @classmethod
    def setup_class(self):
        self.maxDiff = None
        self.uni = unittest.TestCase()
        data = actions.login(self.url, self.pr_key, 0)
        self.token = data['jwtToken']

    def assert_tx_in_block(self, result, jwt_token):
        status = actions.tx_status(self.url,
                                   tools.read_config('test')['wait_tx_status'],
                                   result, jwt_token)
        self.uni.assertNotIn(json.dumps(status), 'errmsg')
        self.uni.assertGreater(status['blockid'], 0)

    def call_contract(self, name, data):
        result = actions.call_contract(self.url, self.pr_key, name,
                                       data, self.token)
        self.assert_tx_in_block(result, self.token)

    def check_page(self, sourse):
        tx = contract.new_page(self.url, self.pr_key, self.token, value=sourse)
        check.is_tx_in_block(self.url, tools.read_config('test')['wait_tx_status'],
                             tx, self.token)
        content = actions.get_content(
            self.url, 'page', tx['name'], '', 1, self.token)
        return content, tx['name']

    def find_position_element_in_tree(self, content_tree, tag_name):
        i = 0
        while i < len(content_tree):
            if content_tree[i]['tag'] == tag_name:
                return i
            i += 1

    def find_position_element_in_tree_by_attribute_name_and_value(self, content_tree, tag_name, attr_name, attr_value):
        i = 0
        while i < len(content_tree):
            if content_tree[i]['tag'] == tag_name:
                if content_tree[i]['attr'][attr_name] == attr_value:
                    return i
            i += 1

    def check_post_api(self, end_point, data, keys):
        end = self.url + end_point
        result = actions.call_post_api(end, data, self.token)
        for key in keys:
            self.uni.assertIn(key, result)
        return result

    def check_get_api(self, end_point, data, keys):
        end = self.url + end_point
        result = actions.call_get_api(end, data, self.token)
        for key in keys:
            self.uni.assertIn(key, result)
        return result

    def test_page_button(self):
        cont = self.pages['button']
        content = self.check_page(cont['code'])
        self.uni.assertEqual(content['tree'][0]['tag'], 'button',
                             'There is no button in content' + str(content['tree']))

    def test_page_button_composite_contract(self):
        cont = self.pages['buttonCompositeContract']
        content = self.check_page(cont['code'])
        part_content = content['tree']
        contract_content = cont['content']
        must_be = dict(tag=part_content[0]['tag'],
                       compositeName=part_content[0]['attr']['composite'][0]['name'],
                       compositeData=part_content[0]['attr']['composite'][0]['data'][0],
                       text=part_content[0]['children'][0]['text'])
        page = dict(tag=contract_content[0]['tag'],
                    compositeName=contract_content[0]['attr']['composite'][0]['name'],
                    compositeData=contract_content[0]['attr']['composite'][0]['data'][0],
                    text=contract_content[0]['children'][0]['text'])
        self.uni.assertDictEqual(
            must_be, page, 'button_composite_contract has problem: ' + str(content['tree']))

    def test_page_button_popup(self):
        cont = self.pages['buttonPopup']
        content = self.check_page(cont['code'])
        part_content = content['tree']
        contract_content = cont['content']
        must_be = dict(tag=part_content[0]['tag'],
                       popupHeader=part_content[0]['attr']['popup']['header'],
                       popupWidth=part_content[0]['attr']['popup']['width'],
                       text=part_content[0]['children'][0]['text'])
        page = dict(tag=contract_content[0]['tag'],
                    popupHeader=contract_content[0]['attr']['popup']['header'],
                    popupWidth=contract_content[0]['attr']['popup']['width'],
                    text=contract_content[0]['children'][0]['text'])
        self.uni.assertDictEqual(
            must_be, page, 'button_popup has problem: ' + str(content['tree']))

    def test_page_addToolButton_popup(self):
        cont = self.pages['addToolButtonPopup']
        content = self.check_page(cont['code'])
        part_content = content['tree']
        contract_content = cont['content']
        must_be = dict(tag=part_content[0]['tag'],
                       title=part_content[0]['attr']['title'],
                       popupHeader=part_content[0]['attr']['popup']['header'],
                       popupWidth=part_content[0]['attr']['popup']['width'])
        page = dict(tag=contract_content[0]['tag'],
                    title=contract_content[0]['attr']['title'],
                    popupHeader=contract_content[0]['attr']['popup']['header'],
                    popupWidth=contract_content[0]['attr']['popup']['width'])
        self.uni.assertDictEqual(
            must_be, page, 'addToolButton_popup has problem: ' + str(content['tree']))

    def test_page_selectorFromDB(self):
        cont = self.pages['selectorFromDB']
        content = self.check_page(cont['code'])
        required_tag_num = self.find_position_element_in_tree(
            content['tree'], 'dbfind')
        must_be = dict(tag='dbfind', data=True)
        page = dict(tag=content['tree'][required_tag_num]['tag'],
                    data=len(content['tree'][required_tag_num]['attr']['columns']) > 2)
        self.uni.assertDictEqual(must_be, page,
                                 'DBfind has problem: ' + str(content['tree']))

    def test_page_selectorFromData(self):
        cont = self.pages['selectorFromData']
        content = self.check_page(cont['code'])
        must_be = dict(tag='data', columns=['gender'], source='myData',
                       select='select', selectName='mySelect', selectSourse='myData')
        page = dict(tag=content['tree'][0]['tag'], columns=content['tree'][0]['attr']['columns'],
                    source=content['tree'][0]['attr']['source'],
                    select=content['tree'][2]['tag'], selectName=content['tree'][2]['attr']['name'],
                    selectSourse=content['tree'][2]['attr']['source'])
        self.uni.assertDictEqual(must_be, page,
                                 'selectorFromData has problem: ' + str(content['tree']))

    def test_page_divs(self):
        cont = self.pages['divs']
        content = self.check_page(cont['code'])
        # outer DIV
        part_content = content['tree'][0]
        # first level inner DIV
        required_inner_tag_num = self.find_position_element_in_tree(
            content['tree'][0]['children'], 'div')
        part_content1 = content['tree'][0]['children'][required_inner_tag_num]
        contract_content1 = cont['content']['children']
        # second level inner DIV
        required_inner2_tag_num = self.find_position_element_in_tree(
            content['tree'][0]['children'][required_inner_tag_num]['children'], 'div')
        part_content2 = content['tree'][0]['children'][required_inner_tag_num]['children'][required_inner2_tag_num]
        contract_content2 = cont['content']['children']['children']
        must_be = dict(firstDivTag=part_content['tag'],
                       firstDivClass=part_content['attr']['class'],
                       innerDivTag1=part_content1['tag'],
                       innerDivClass1=part_content1['attr']['class'],
                       innerDivTag2=part_content2['tag'],
                       innerDivClass2=part_content2['attr']['class'],
                       childrenText=part_content2['children'][0]['text'])
        page = dict(firstDivTag=cont['content']['tag'],
                    firstDivClass=cont['content']['attr']['class'],
                    innerDivTag1=contract_content1['tag'],
                    innerDivClass1=contract_content1['attr']['class'],
                    innerDivTag2=contract_content2['tag'],
                    innerDivClass2=contract_content2['attr']['class'],
                    childrenText=contract_content2['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'divs has problem: ' + str(content['tree']))
        
    def test_page_show(self):
        cont = self.pages['show']
        content = self.check_page(cont['code'])
        tree = content['tree']
        result = None
        for part in tree:
            if part['tag'] == 'div':
                result = part['attr']
        self.uni.assertEqual(part['attr'], cont['content']['attr'],
                             'show has problem: ' + str(content['tree']))
        
    def test_page_show2(self):
        cont = self.pages['show2']
        content = self.check_page(cont['code'])
        tree = content['tree']
        result = None
        for part in tree:
            if part['tag'] == 'div':
                result = part['attr']
        self.uni.assertEqual(part['attr'], cont['content']['attr'],
                             'show has problem: ' + str(content['tree']))
        
    def test_page_error_redirect(self):
        cont = self.pages['errorRedirect']
        content = self.check_page(cont['code'])
        tree = content['tree']
        result = None
        for part in tree:
            if part['tag'] == 'button':
                result = part['attr']
        self.uni.assertEqual(part['attr'], cont['content']['attr'],
                             'show has problem: ' + str(content['tree']))
    
    def test_page_hide(self):
        cont = self.pages['hide']
        content = self.check_page(cont['code'])
        tree = content['tree'][0]['children']
        result = None
        for part in tree:
            if part['tag'] == 'div':
                result = part['attr']
        self.uni.assertEqual(part['attr'], cont['content']['attr'],
                             'show has problem: ' + str(content['tree']))

    def test_page_varAsIs(self):
        cont = self.pages['varAsIs']
        contract_content = cont['content']
        content = self.check_page(cont['code'])
        part_content = content['tree']
        required_tag_num = self.find_position_element_in_tree(
            content['tree'], 'span')
        span = part_content[required_tag_num]
        required_tag_num = self.find_position_element_in_tree(
            content['tree'], 'em')
        em = part_content[required_tag_num]
        required_tag_num = self.find_position_element_in_tree(
            content['tree'], 'div')
        div = part_content[required_tag_num]
        must_be = dict(tagSpan=contract_content[0]['tag'],
                       childrenSpanText=contract_content[0]['children'][0]['text'],
                       tagEm=contract_content[1]['tag'],
                       childrenEmText=contract_content[1]['children'][0]['text'],
                       tagDiv=contract_content[2]['tag'],
                       childrenDivText=contract_content[2]['children'][0]['text'])
        page = dict(tagSpan=span['tag'],
                    childrenSpanText=span['children'][0]['text'],
                    tagEm=em['tag'],
                    childrenEmText=em['children'][0]['text'],
                    tagDiv=div['tag'],
                    childrenDivText=div['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'varAsIs has problem: ' + str(content['tree']))

    def test_page_setVar(self):
        cont = self.pages['setVar']
        content = self.check_page(cont['code'])
        required_tag_num = self.find_position_element_in_tree(
            content['tree'], 'div')
        part_content = content['tree'][required_tag_num]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       childrenText=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    childrenText=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'setVar has problem: ' + str(content['tree']))

    def test_page_input(self):
        cont = self.pages['input']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       inputClass=part_content['attr']['class'],
                       name=part_content['attr']['name'],
                       placeholder=part_content['attr']['placeholder'],
                       type=part_content['attr']['type'])
        page = dict(tag=contract_content['tag'],
                    inputClass=contract_content['attr']['class'],
                    name=contract_content['attr']['name'],
                    placeholder=contract_content['attr']['placeholder'],
                    type=contract_content['attr']['type'])
        self.uni.assertDictEqual(must_be, page,
                                 'input has problem: ' + str(content['tree']))

    def test_page_menuGroup(self):
        cont = self.pages['menuGroup']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        menu_item1 = contract_content['children'][0]
        menu_item2 = contract_content['children'][1]
        required_num_menu_item1 = self.find_position_element_in_tree_by_attribute_name_and_value(part_content['children'],
                                                                                                 'menuitem', 'title',
                                                                                                 menu_item1['attr']['title'])
        required_num_menu_item2 = self.find_position_element_in_tree_by_attribute_name_and_value(part_content['children'],
                                                                                                 'menuitem', 'title',
                                                                                                 menu_item2['attr']['title'])
        part_content1 = part_content['children'][required_num_menu_item1]
        part_content2 = part_content['children'][required_num_menu_item2]
        must_be = dict(menuTag=part_content['tag'],
                       name=part_content['attr']['name'],
                       title=part_content['attr']['title'],
                       menuItemTag1=part_content1['tag'],
                       menuItemPage1=part_content1['attr']['page'],
                       menuItemTitle1=part_content1['attr']['title'],
                       menuItemTag2=part_content2['tag'],
                       menuItemPage2=part_content2['attr']['page'],
                       menuItemTitle2=part_content2['attr']['title'])
        page = dict(menuTag=contract_content['tag'],
                    name=contract_content['attr']['name'],
                    title=contract_content['attr']['title'],
                    menuItemTag1=part_content1['tag'],
                    menuItemPage1=menu_item1['attr']['page'],
                    menuItemTitle1=menu_item1['attr']['title'],
                    menuItemTag2=part_content2['tag'],
                    menuItemPage2=menu_item2['attr']['page'],
                    menuItemTitle2=menu_item2['attr']['title'])
        self.uni.assertDictEqual(must_be, page,
                                 'menuGroup has problem: ' + str(content['tree']))

    def test_page_linkPage(self):
        cont = self.pages['linkPage']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       linkPageClass=part_content['attr']['class'],
                       page=part_content['attr']['page'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    linkPageClass=contract_content['attr']['class'],
                    page=contract_content['attr']['page'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'linkPage has problem: ' + str(content['tree']))

    def test_page_ecosysParam(self):
        cont = self.pages['ecosysParam']
        content = self.check_page(cont['code'])
        part_сontent = content['tree'][0]
        contract_сontent = cont['content']
        must_be = dict(tag=part_сontent['tag'],
                       text=part_сontent['children'][0]['text'])
        page = dict(tag=contract_сontent['tag'],
                    text=contract_сontent['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'ecosysParam has problem: ' + str(content['tree']))

    def test_page_paragraph(self):
        cont = self.pages['paragraph']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'paragraph has problem: ' + str(content['tree']))

    def test_page_getVar(self):
        cont = self.pages['getVar']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'getVar has problem: ' + str(content['tree']))

    def test_page_hint(self):
        page = self.pages['hint']
        content = self.check_page(page['code'])
        part_content = content['tree'][0]
        page_content = page['content']
        must_be = dict(tag=part_content['tag'],
                       icon=part_content['attr']['icon'],
                       title=part_content['attr']['title'],
                       text=part_content['attr']['text'])
        page = dict(tag=page_content['tag'],
                    icon=page_content['attr']['icon'],
                    title=page_content['attr']['title'],
                    text=page_content['attr']['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'getVar has problem: ' + str(content['tree']))

    def test_page_iff(self):
        cont = self.pages['iff']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'iff has problem: ' + str(content['tree']))

    def test_page_orr(self):
        cont = self.pages['orr']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'orr has problem: ' + str(content['tree']))

    def test_page_andd(self):
        cont = self.pages['andd']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       text=part_content['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'andd has problem: ' + str(content['tree']))

    def test_page_form(self):
        cont = self.pages['form']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        part_content1 = content['tree'][0]['children'][0]['children'][0]
        contract_content = cont['content']
        contract_content1 = cont['content']['children'][0]['children'][0]
        must_be = dict(formTag=part_content['tag'],
                       spanTag=part_content['children'][0]['tag'],
                       spanText=part_content1['text'])
        page = dict(formTag=contract_content['tag'],
                    spanTag=contract_content['children'][0]['tag'],
                    spanText=contract_content1['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'form has problem: ' + str(content['tree']))

    def test_page_label(self):
        cont = self.pages['label']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       labelFor=part_content['attr']['for'])
        page = dict(tag=contract_content['tag'],
                    labelFor=contract_content['attr']['for'])
        self.uni.assertDictEqual(must_be, page,
                                 'label has problem: ' + str(content['tree']))

    def test_page_span(self):
        cont = self.pages['span']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'span has problem: ' + str(content['tree']))

    def test_page_langRes(self):
        lang = 'lang_' + tools.generate_random_name()
        data = {'Name': lang,
                'Trans': '{"en": "Lang_en", "ru" : "Язык", "fr-FR": "Monde_fr-FR", "de": "Welt_de"}'}
        res = actions.call_contract(
            self.url, self.pr_key, 'NewLang', data, self.token)
        self.assert_tx_in_block(res, self.token)
        world = 'world_' + tools.generate_random_name()
        data = {'Name': world,
                'Trans': '{"en": "World_en", "ru" : "Мир_ru", "fr-FR": "Monde_fr-FR", "de": "Welt_de"}'}
        res = actions.call_contract(
            self.url, self.pr_key, 'NewLang', data, self.token)
        self.assert_tx_in_block(res, self.token)
        cont = self.pages['langRes']
        content = self.check_page(
            'LangRes(' + lang + ') LangRes(' + world + ', ru)')

    def test_page_inputErr(self):
        cont = self.pages['inputErr']
        content = self.check_page(cont['code'])
        # iterating response elements
        required_tag_num = self.find_position_element_in_tree(
            content['tree'], 'inputerr')
        part_content = content['tree'][required_tag_num]['tag']
        self.uni.assertEqual(part_content, cont['content']['tag'],
                             'Error in content ' + str(content['tree']))
        part_content = content['tree'][required_tag_num]['attr']
        contract_content = cont['content']['attr']
        must_be = dict(maxlength=part_content['maxlength'],
                       name=part_content['name'],
                       minlength=part_content['minlength'])
        page = dict(maxlength=contract_content['maxlength'],
                    name=contract_content['name'],
                    minlength=contract_content['minlength'])
        self.uni.assertDictEqual(must_be, page,
                                 'inputErr has problem: ' + str(content['tree']))

    def test_page_include(self):
        name = 'Block_' + tools.generate_random_name()
        data = {'Name': name, 'ApplicationId': 1,
                'Value': 'Hello page!', 'Conditions': 'true'}
        res = actions.call_contract(
            self.url, self.pr_key, 'NewBlock', data, self.token)
        self.assert_tx_in_block(res, self.token)
        cont = self.pages['include']
        content = self.check_page('Include(' + name + ')')
        self.uni.assertEqual(content['tree'][0]['text'], cont['content'][0]['text'],
                             'include has problem: ' + str(content['tree']))

    def test_page_inputImage(self):
        cont = self.pages['inputImage']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content'][0]
        must_be = dict(tag=part_content['tag'],
                       name=part_content['attr']['name'],
                       ratio=part_content['attr']['ratio'],
                       width=part_content['attr']['width'])
        page = dict(tag=contract_content['tag'],
                    name=contract_content['attr']['name'],
                    ratio=contract_content['attr']['ratio'],
                    width=contract_content['attr']['width'])
        self.uni.assertDictEqual(must_be, page,
                                 'inputErr has problem: ' + str(content['tree']))

    def test_page_alert(self):
        cont = self.pages['alert']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        part_content1 = content['tree'][0]['attr']['alert']
        contract_content1 = cont['content']['attr']['alert']
        must_be = dict(tag=part_content['tag'],
                       cancelbutton=part_content1['cancelbutton'],
                       confirmbutton=part_content1['confirmbutton'],
                       icon=part_content1['icon'],
                       text=part_content1['text'])
        page = dict(tag=contract_content['tag'],
                    cancelbutton=contract_content1['cancelbutton'],
                    confirmbutton=contract_content1['confirmbutton'],
                    icon=contract_content1['icon'],
                    text=contract_content1['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'alert has problem: ' + str(content['tree']))

    def test_page_table(self):
        cont = self.pages['table']
        content = self.check_page(cont['code'])
        must_be = dict(tag='dbfind', source='mysrc',
                       tag2='table', columns=[{'Name': 'name', 'Title': 'Name'}, {'Name': 'value', 'Title': 'Value'},
                                              {'Name': 'conditions', 'Title': 'Conditions'}])
        page = dict(tag=content['tree'][0]['tag'], source=content['tree'][1]['attr']['source'],
                    tag2=content['tree'][1]['tag'],
                    columns=content['tree'][1]['attr']['columns'])
        self.uni.assertDictEqual(must_be, page,
                                 'selectorFromData has problem: ' + str(content['tree']))

    def test_page_kurs(self):
        cont = self.pages['kurs']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content'][0]
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'kurs has problem: ' + str(content['tree']))

    def test_page_strong(self):
        cont = self.pages['strong']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content'][0]
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'strong has problem: ' + str(content['tree']))

    def test_page_getColumnType(self):
        cont = self.pages['getColumnType']
        content = self.check_page(cont['code'])
        self.uni.assertEqual(str(content['tree'][0]['text']), cont['content']['text'],
                             'getColumnType has problem: ' + str(content['tree']))

    def test_page_sys_var_isMobile(self):
        cont = self.pages['sys_var_isMobile']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content'][0]
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'isMobile has problem: ' + str(content['tree']))

    def test_page_sys_var_roleID(self):
        cont = self.pages['sys_var_roleID']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content'][0]
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'roleID has problem: ' + str(content['tree']))

    def test_page_sys_var_ecosystemID(self):
        cont = self.pages['sys_var_ecosystemID']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content'][0]
        must_be = dict(tag=part_content['tag'],
                       text=part_content['children'][0]['text'])
        page = dict(tag=contract_content['tag'],
                    text=contract_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'ecosystemID has problem: ' + str(content['tree']))

    def test_page_sys_var_ecosystem_name(self):
        # get ecosystem name from api
        count = api.ecosystems(self.url, self.token)['number']
        res = api.list(self.url, self.token, 'ecosystems', limit=count)
        id = 1
        i = 0
        required_ecosys_name = ''
        while i < int(res['count']):
            if int(res['list'][i]['id']) == id:
                required_ecosys_name = res['list'][i]['name']
            i += 1
        # test
        cont = self.pages['sys_var_ecosystem_name']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        must_be = dict(tag='em',
                       text=required_ecosys_name)
        page = dict(tag=part_content['tag'],
                    text=part_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'ecosystem_name has problem: ' + str(content['tree']))

    def test_page_sys_var_key_id(self):
        content = self.check_page('Em(EcosysParam(founder_account))')
        founder_acc = content['tree'][0]['children'][0]['text']
        cont = self.pages['sys_var_keyID']
        content = self.check_page(cont['code'])
        key_id = content['tree'][0]['children'][0]['text']
        self.uni.assertEqual(key_id, founder_acc,
                             'key_id has problem: ' + cont['content'] + '. Content = ' + str(
                                 content['tree']))

    def test_page_sys_var_guest_key(self):
        cont = self.pages['sys_var_guest_key']
        content = self.check_page(cont['code'])
        guest_key = content['tree'][0]['children'][0]['text']
        self.uni.assertEqual(guest_key, cont['content'],
                             'guest_key has problem: ' + cont['content'] + '. Content = ' + str(
                                 content['tree']))

    def test_db_find_where_count(self):
        cont = self.pages['dbfindWhereCount']
        content = self.check_page(cont['code'])
        required_num = self.find_position_element_in_tree(
            content['tree'], 'em')
        page = content['tree'][required_num]['children'][0]['text']
        self.uni.assertEqual(cont['content'], page,
                             'dbfind_where_count has problem: ' + cont['content'] + '. Content = ' + str(
            content['tree']))

    def test_db_find_where_id_count(self):
        cont = self.pages['dbfindWhereIdCount']
        content = self.check_page(cont['code'])
        required_num = self.find_position_element_in_tree(
            content['tree'], 'em')
        page = content['tree'][required_num]['children'][0]['text']
        self.uni.assertEqual(cont['content'], page,
                             'dbfind_whereId_count has problem: ' + cont['content'] + '. Content = ' + str(
            content['tree']))

    def test_binary(self):
        # this test has not fixture
        name = 'image_' + tools.generate_random_name()
        app_id = '1'
        path = os.path.join(os.getcwd(), 'fixtures', 'image2.jpg')
        with open(path, 'rb') as f:
            file = f.read()
        data = {'Name': name, 'ApplicationId': app_id, 'Data': file}
        resp = actions.call_contract(
            self.url, self.pr_key, 'UploadBinary', data, self.token)
        self.assert_tx_in_block(resp, self.token)
        # test
        member_id = actions.get_parameter_value(
            self.url, 'founder_account', self.token)
        last_rec = actions.get_count(self.url, 'binaries', self.token)
        content = self.check_page('Binary(Name: ' + name + ', AppID: ' + app_id +
                                  ', MemberID: ' + member_id + ')')
        msg = 'test_binary has problem. Content = ' + str(content['tree'])
        file_hash = '122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05'
        self.uni.assertEqual('/data/1_binaries/'+last_rec+'/data/' + file_hash,
                             content['tree'][0]['text'])

    def test_binary_by_id(self):
        # this test has not fixture
        name = 'image_' + tools.generate_random_name()
        app_id = '1'
        path = os.path.join(os.getcwd(), 'fixtures', 'image2.jpg')
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {'Name': name, 'ApplicationId': app_id, 'Data': file}
        resp = actions.call_contract(
            self.url, self.pr_key, 'UploadBinary', data, self.token)
        res = self.assert_tx_in_block(resp, self.token)
        # test
        last_rec = actions.get_count(self.url, 'binaries', self.token)
        content = self.check_page('Binary().ById(' + last_rec + ')')
        msg = 'test_binary has problem. Content = ' + str(content['tree'])
        file_hash = '122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05'
        self.uni.assertEqual('/data/1_binaries/' + last_rec + '/data/' + file_hash,
                             content['tree'][0]['text'])

    def test_image_binary(self):
        # this test has not fixture
        name = 'image_' + tools.generate_random_name()
        app_id = '1'
        path = os.path.join(os.getcwd(), 'fixtures', 'image2.jpg')
        with open(path, 'rb') as f:
            file = f.read()
        data = {'Name': name, 'ApplicationId': app_id, 'Data': file}
        resp = actions.call_contract(
            self.url, self.pr_key, 'UploadBinary', data, self.token)
        self.assert_tx_in_block(resp, self.token)
        # test
        member_id = actions.get_parameter_value(
            self.url, 'founder_account', self.token)
        last_rec = actions.get_count(self.url, 'binaries', self.token)
        content = self.check_page("Image(Binary(Name: " + name + ", AppID: " + app_id +
                                  ", MemberID: " + member_id + "))")
        part_content = content['tree'][0]
        file_hash = '122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05'
        must_be = dict(tag=part_content['tag'],
                       src=part_content['attr']['src'])
        page = dict(tag='image',
                    src='/data/1_binaries/' + last_rec + '/data/' + file_hash)
        self.uni.assertDictEqual(must_be, page,
                                 'test_image_binary has problem: ' + str(content['tree']))

    def test_image_binary_by_id(self):
        # this test has not fixture
        name = 'image_' + tools.generate_random_name()
        app_id = '1'
        path = os.path.join(os.getcwd(), 'fixtures', 'image2.jpg')
        with open(path, 'rb') as f:
            file = f.read()
        data = {'Name': name, 'ApplicationId': app_id, 'Data': file}
        resp = actions.call_contract(
            self.url, self.pr_key, 'UploadBinary', data, self.token)
        self.assert_tx_in_block(resp, self.token)
        # test
        last_rec = actions.get_count(self.url, 'binaries', self.token)
        content = self.check_page('Image(Binary().ById("{last_rec}"))'.format(last_rec=last_rec))
        part_сontent = content['tree'][0]
        file_hash = '122e37a4a7737e0e8663adad6582fc355455f8d5d35bd7a08ed00c87f3e5ca05'
        must_be = dict(tag=part_сontent['tag'],
                       src=part_сontent['attr']['src'])
        page = dict(tag='image',
                    src='/data/1_binaries/' + last_rec + '/data/' + file_hash)
        self.uni.assertDictEqual(must_be, page,
                                 'test_image_binary_by_id has problem: ' + str(content['tree']))

    def test_address(self):
        cont = self.pages['address']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tagOwner=contract_content['tag'],
                       tag=contract_content['children'][0]['tag'],
                       text=contract_content['children'][0]['text'])
        page = dict(tagOwner=part_content['tag'],
                    tag=part_content['children'][0]['tag'],
                    text=part_content['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'address has problem: ' + str(content['tree']))

    def test_money(self):
        cont = self.pages['money']
        content1 = self.check_page(cont['code1'])
        content2 = self.check_page(cont['code2'])
        part_content1 = content1['tree'][0]
        part_content2 = content2['tree'][0]
        contract_content1 = cont['content1']
        contract_content2 = cont['content2']
        must_be = dict(tagOwner1=contract_content1['tag'],
                       tag1=contract_content1['children'][0]['tag'],
                       text1=contract_content1['children'][0]['text'],
                       tagOwner2=contract_content2['tag'],
                       tag2=contract_content2['children'][0]['tag'],
                       text2=contract_content2['children'][0]['text'])
        page = dict(tagOwner1=part_content1['tag'],
                    tag1=part_content1['children'][0]['tag'],
                    text1=part_content1['children'][0]['text'],
                    tagOwner2=part_content2['tag'],
                    tag2=part_content2['children'][0]['tag'],
                    text2=part_content2['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page,
                                 'money has problem: \n' + str(content1['tree']) + '\n' + str(
                                     content2['tree']))

    def test_calculate(self):
        cont = self.pages['calculate']
        # Set for type of money
        money_content1 = self.check_page(cont['moneyCode1'])
        part_money_content1 = money_content1['tree'][0]
        contract_money_content1 = cont['moneyContent1']
        money_content2 = self.check_page(cont['moneyCode2'])
        part_money_content2 = money_content2['tree'][0]
        contract_money_content2 = cont['moneyContent2']
        money_content3 = self.check_page(cont['moneyCode3'])
        part_money_content3 = money_content3['tree'][0]
        contract_money_content3 = cont['moneyContent3']
        money_content4 = self.check_page(cont['moneyCode4'])
        part_money_content4 = money_content4['tree'][0]
        contract_money_content4 = cont['moneyContent4']
        money_content5 = self.check_page(cont['moneyCode5'])
        part_money_content5 = money_content5['tree'][0]
        contract_money_content5 = cont['moneyContent5']
        money_content6 = self.check_page(cont['moneyCode6'])
        part_money_content6 = money_content6['tree'][0]
        contract_money_content6 = cont['moneyContent6']
        moneyContent7 = self.check_page(cont['moneyCode7'])
        partMoneyContent7 = moneyContent7['tree'][0]
        contractMoneyContent7 = cont['moneyContent7']
        moneyContent8 = self.check_page(cont['moneyCode8'])
        partMoneyContent8 = moneyContent8['tree'][0]
        contractMoneyContent8 = cont['moneyContent8']
        moneyContent9 = self.check_page(cont['moneyCode9'])
        partMoneyContent9 = moneyContent9['tree'][0]
        contractMoneyContent9 = cont['moneyContent9']
        moneyContent10 = self.check_page(cont['moneyCode10'])
        partMoneyContent10 = moneyContent10['tree'][0]
        contractMoneyContent10 = cont['moneyContent10']
        moneyContent11 = self.check_page(cont['moneyCode11'])
        partMoneyContent11 = moneyContent11['tree'][0]
        contractMoneyContent11 = cont['moneyContent11']
        moneyContent12 = self.check_page(cont['moneyCode12'])
        partMoneyContent12 = moneyContent12['tree'][0]
        contractMoneyContent12 = cont['moneyContent12']
        moneyContent13 = self.check_page(cont['moneyCode13'])
        partMoneyContent13 = moneyContent13['tree'][0]
        contractMoneyContent13 = cont['moneyContent13']
        moneyContent14 = self.check_page(cont['moneyCode14'])
        partMoneyContent14 = moneyContent14['tree'][0]
        contractMoneyContent14 = cont['moneyContent14']
        moneyContent15 = self.check_page(cont['moneyCode15'])
        partMoneyContent15 = moneyContent15['tree'][0]
        contractMoneyContent15 = cont['moneyContent15']
        # Set for type of money
        floatContent1 = self.check_page(cont['floatCode1'])
        partFloatContent1 = floatContent1['tree'][0]
        contractFloatContent1 = cont['floatContent1']
        floatContent2 = self.check_page(cont['floatCode2'])
        partFloatContent2 = floatContent2['tree'][0]
        contractFloatContent2 = cont['floatContent2']
        floatContent3 = self.check_page(cont['floatCode3'])
        partFloatContent3 = floatContent3['tree'][0]
        contractFloatContent3 = cont['floatContent3']
        floatContent4 = self.check_page(cont['floatCode4'])
        partFloatContent4 = floatContent4['tree'][0]
        contractFloatContent4 = cont['floatContent4']
        floatContent5 = self.check_page(cont['floatCode5'])
        partFloatContent5 = floatContent5['tree'][0]
        contractFloatContent5 = cont['floatContent5']
        floatContent6 = self.check_page(cont['floatCode6'])
        partFloatContent6 = floatContent6['tree'][0]
        contractFloatContent6 = cont['floatContent6']
        floatContent7 = self.check_page(cont['floatCode7'])
        partFloatContent7 = floatContent7['tree'][0]
        contractFloatContent7 = cont['floatContent7']
        floatContent8 = self.check_page(cont['floatCode8'])
        partFloatContent8 = floatContent8['tree'][0]
        contractFloatContent8 = cont['floatContent8']
        floatContent9 = self.check_page(cont['floatCode9'])
        partFloatContent9 = floatContent9['tree'][0]
        contractFloatContent9 = cont['floatContent9']
        floatContent10 = self.check_page(cont['floatCode10'])
        partFloatContent10 = floatContent10['tree'][0]
        contractFloatContent10 = cont['floatContent10']
        floatContent11 = self.check_page(cont['floatCode11'])
        partFloatContent11 = floatContent11['tree'][0]
        contractFloatContent11 = cont['floatContent11']
        floatContent12 = self.check_page(cont['floatCode12'])
        partFloatContent12 = floatContent12['tree'][0]
        contractFloatContent12 = cont['floatContent12']
        floatContent13 = self.check_page(cont['floatCode13'])
        partFloatContent13 = floatContent13['tree'][0]
        contractFloatContent13 = cont['floatContent13']
        floatContent14 = self.check_page(cont['floatCode14'])
        partFloatContent14 = floatContent14['tree'][0]
        contractFloatContent14 = cont['floatContent14']
        floatContent15 = self.check_page(cont['floatCode15'])
        partFloatContent15 = floatContent15['tree'][0]
        contractFloatContent15 = cont['floatContent15']
        # Set for type of int
        intContent1 = self.check_page(cont['intCode1'])
        partIntContent1 = intContent1['tree'][0]
        contractIntContent1 = cont['intContent1']
        intContent2 = self.check_page(cont['intCode2'])
        partIntContent2 = intContent2['tree'][0]
        contractIntContent2 = cont['intContent2']
        intContent3 = self.check_page(cont['intCode3'])
        partIntContent3 = intContent3['tree'][0]
        contractIntContent3 = cont['intContent3']
        intContent4 = self.check_page(cont['intCode4'])
        partIntContent4 = intContent4['tree'][0]
        contractIntContent4 = cont['intContent4']
        intContent5 = self.check_page(cont['intCode5'])
        partIntContent5 = intContent5['tree'][0]
        contractIntContent5 = cont['intContent5']
        intContent6 = self.check_page(cont['intCode6'])
        partIntContent6 = intContent6['tree'][0]
        contractIntContent6 = cont['intContent6']
        # Set wrong type
        wrongContent1 = self.check_page(cont['wrongCode1'])
        partWrongContent1 = wrongContent1['tree'][0]
        contractWrongContent1 = cont['wrongContent1']
        must_be = dict(money1=contract_money_content1['children'][0]['text'],
                       money2=contract_money_content2['children'][0]['text'],
                       money3=contract_money_content3['children'][0]['text'],
                       money4=contract_money_content4['children'][0]['text'],
                       money5=contract_money_content5['children'][0]['text'],
                       money6=contract_money_content6['children'][0]['text'],
                       money7=contractMoneyContent7['children'][0]['text'],
                       money8=contractMoneyContent8['children'][0]['text'],
                       money9=contractMoneyContent9['children'][0]['text'],
                       money10=contractMoneyContent10['children'][0]['text'],
                       money11=contractMoneyContent11['children'][0]['text'],
                       money12=contractMoneyContent12['children'][0]['text'],
                       money13=contractMoneyContent13['children'][0]['text'],
                       money14=contractMoneyContent14['children'][0]['text'],
                       money15=contractMoneyContent15['children'][0]['text'],
                       float1=contractFloatContent1['children'][0]['text'],
                       float2=contractFloatContent2['children'][0]['text'],
                       float3=contractFloatContent3['children'][0]['text'],
                       float4=contractFloatContent4['children'][0]['text'],
                       float5=contractFloatContent5['children'][0]['text'],
                       float6=contractFloatContent6['children'][0]['text'],
                       float7=contractFloatContent7['children'][0]['text'],
                       float8=contractFloatContent8['children'][0]['text'],
                       float9=contractFloatContent9['children'][0]['text'],
                       float10=contractFloatContent10['children'][0]['text'],
                       float11=contractFloatContent11['children'][0]['text'],
                       float12=contractFloatContent12['children'][0]['text'],
                       float13=contractFloatContent13['children'][0]['text'],
                       float14=contractFloatContent14['children'][0]['text'],
                       float15=contractFloatContent15['children'][0]['text'],
                       int1=contractIntContent1['children'][0]['text'],
                       int2=contractIntContent2['children'][0]['text'],
                       int3=contractIntContent3['children'][0]['text'],
                       int4=contractIntContent4['children'][0]['text'],
                       int5=contractIntContent5['children'][0]['text'],
                       int6=contractIntContent6['children'][0]['text'],
                       wrong1=contractWrongContent1['children'][0]['text'])
        page = dict(money1=part_money_content1['children'][0]['text'],
                    money2=part_money_content2['children'][0]['text'],
                    money3=part_money_content3['children'][0]['text'],
                    money4=part_money_content4['children'][0]['text'],
                    money5=part_money_content5['children'][0]['text'],
                    money6=part_money_content6['children'][0]['text'],
                    money7=partMoneyContent7['children'][0]['text'],
                    money8=partMoneyContent8['children'][0]['text'],
                    money9=partMoneyContent9['children'][0]['text'],
                    money10=partMoneyContent10['children'][0]['text'],
                    money11=partMoneyContent11['children'][0]['text'],
                    money12=partMoneyContent12['children'][0]['text'],
                    money13=partMoneyContent13['children'][0]['text'],
                    money14=partMoneyContent14['children'][0]['text'],
                    money15=partMoneyContent15['children'][0]['text'],
                    float1=partFloatContent1['children'][0]['text'],
                    float2=partFloatContent2['children'][0]['text'],
                    float3=partFloatContent3['children'][0]['text'],
                    float4=partFloatContent4['children'][0]['text'],
                    float5=partFloatContent5['children'][0]['text'],
                    float6=partFloatContent6['children'][0]['text'],
                    float7=partFloatContent7['children'][0]['text'],
                    float8=partFloatContent8['children'][0]['text'],
                    float9=partFloatContent9['children'][0]['text'],
                    float10=partFloatContent10['children'][0]['text'],
                    float11=partFloatContent11['children'][0]['text'],
                    float12=partFloatContent12['children'][0]['text'],
                    float13=partFloatContent13['children'][0]['text'],
                    float14=partFloatContent14['children'][0]['text'],
                    float15=partFloatContent15['children'][0]['text'],
                    int1=partIntContent1['children'][0]['text'],
                    int2=partIntContent2['children'][0]['text'],
                    int3=partIntContent3['children'][0]['text'],
                    int4=partIntContent4['children'][0]['text'],
                    int5=partIntContent5['children'][0]['text'],
                    int6=partIntContent6['children'][0]['text'],
                    wrong1=partWrongContent1['children'][0]['text'])
        self.uni.assertDictEqual(must_be, page, 'calculate has problem!')

    def test_arrayToSource(self):
        cont = self.pages['arrayToSource']
        content = self.check_page(cont['code'])
        part_content = content['tree'][0]
        contract_content = cont['content']
        must_be = dict(tag=part_content['tag'],
                       data1=part_content['attr']['data'][0],
                       data2=part_content['attr']['data'][1],
                       data3=part_content['attr']['data'][2],
                       data4=part_content['attr']['data'][3],
                       data5=part_content['attr']['data'][4],
                       source=part_content['attr']['source'])
        page = dict(tag=contract_content['tag'],
                    data1=contract_content['attr']['data'][0],
                    data2=contract_content['attr']['data'][1],
                    data3=contract_content['attr']['data'][2],
                    data4=contract_content['attr']['data'][3],
                    data5=contract_content['attr']['data'][4],
                    source=contract_content['attr']['source'])
        self.uni.assertDictEqual(must_be, page,
                                 'arrayToSource has problem: \n' + str(content['tree']))

    def test_getHistoryContract(self):
        # it test has not fixture
        # create contract
        replaced_string = 'variable_for_replace'
        code = '''
        {
            data{}
            conditions{}
            action{ var %s int }
        }
        ''' % replaced_string
        tx = contract.new_contract(
            self.url, self.pr_key, self.token, source=code)
        check.is_tx_in_block(self.url, self.wait, tx, self.token)
        # change contract
        id = actions.get_object_id(
            self.url, tx['name'], 'contracts', self.token)
        replaced_code = tx['code'].replace(replaced_string, 'new_var')
        new_code = 'contract {name} {code}'.format(name=tx['name'],
                                                   code=replaced_code)
        data = {'Id': id, 'Value': new_code}
        self.call_contract('EditContract', data)
        # test
        content = self.check_page(
            'GetHistory(src, contracts, "' + str(id) + '")')
        part_content = content['tree'][0]['attr']['data'][0]
        self.uni.assertIn(replaced_string, str(part_content),
                          'getHistoryContract has problem: ' + str(content['tree']))


    def test_transactionInfo(self):
        # it test has not fixture
        res = contract.new_contract(self.url,
                                    self.pr_key,
                                    self.token)
        content = self.check_page(
            'Span(TransactionInfo({hash}))'.format(hash=res['hash']))
        part_content = content['tree'][0]['children'][0]['text']
        expected_str = '"contract":"@1NewContract","params":{"ApplicationId":1'
        self.uni.assertIn(expected_str, str(part_content),
                          'transactionInfo has problem: ' + str(content['tree']))

    def test_DBFindSortedKeys(self):
        table = 'keys'
        # create new ecosystem
        tx_ecos = contract.new_ecosystem(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_ecos, self.token)
        # get data from db
        db_res = db.get_all_sorted_records_from_table(self.db1, table)
        # get hash from data
        expected_hash = tools.get_hash_sha256(str(db_res))
        cont = self.pages['DBFindSortedKeys']
        # create page with content
        _, page_name = self.check_page(cont['code'])
        # test
        expected_list = {}
        actual_list = {}
        i = 0
        while i < 10:
            expected_list[i] = expected_hash
            # get content from page
            content = actions.get_content(
                self.url, 'page', page_name, '', 1, self.token)
            dbfind_list = []
            dbfind_data = content['tree'][0]['attr']['data']
            for el in dbfind_data:
                id = int(el[0])
                ecos = int(el[1])
                t = (id, ecos)
                dbfind_list.append(t)
            actual_hash = tools.get_hash_sha256(str(dbfind_list))
            actual_list[i] = actual_hash
            i += 1
        self.uni.assertDictEqual(expected_list, actual_list, 'Hashes is not equals')

    def test_DBFindSortedMembers(self):
        table = 'members'
        # create new ecosystem
        tx_ecos = contract.new_ecosystem(self.url, self.pr_key, self.token)
        check.is_tx_in_block(self.url, self.wait, tx_ecos, self.token)
        # get data from db
        db_res = db.get_all_sorted_records_from_table(self.db1, table)
        # get hash from data
        expected_hash = tools.get_hash_sha256(str(db_res))
        cont = self.pages['DBFindSortedMembers']
        # create page with content
        _, page_name = self.check_page(cont['code'])
        # test
        expected_list = {}
        actual_list = {}
        i = 0
        while i < 10:
            expected_list[i] = expected_hash
            # get content from page
            content = actions.get_content(
                self.url, 'page', page_name, '', 1, self.token)
            dbfind_list = []
            dbfind_data = content['tree'][0]['attr']['data']
            for el in dbfind_data:
                id = int(el[0])
                ecos = int(el[1])
                t = (id, ecos)
                dbfind_list.append(t)
            actual_hash = tools.get_hash_sha256(str(dbfind_list))
            actual_list[i] = actual_hash
            i += 1
        self.uni.assertDictEqual(expected_list, actual_list, 'Hashes is not equals')

    def test_DBFindSortedPages(self):
        table = 'pages'
        # create page with content
        cont = self.pages['DBFindSortedPages']
        _, page_name = self.check_page(cont['code'])
        # get data from db
        db_res = db.get_all_sorted_records_from_table(self.db1, table)
        # get hash from data
        expected_hash = tools.get_hash_sha256(str(db_res))
        # test
        expected_list = {}
        actual_list = {}
        i = 0
        while i < 10:
            expected_list[i] = expected_hash
            # get content from page
            content = actions.get_content(
                self.url, 'page', page_name, '', 1, self.token)
            dbfind_list = []
            dbfind_data = content['tree'][0]['attr']['data']
            for el in dbfind_data:
                id = int(el[0])
                name = el[1]
                t = (id, name)
                dbfind_list.append(t)
            actual_hash = tools.get_hash_sha256(str(dbfind_list))
            actual_list[i] = actual_hash
            i += 1
        self.uni.assertDictEqual(expected_list, actual_list, 'Hashes is not equals')

    def test_DBFindSortedUserTable(self):
        # create user table
        table = tools.generate_random_name()
        columns = '''[{"name":"name","type":"varchar",
                       "index": "1",  "conditions":"true"}]'''
        tx_cont = contract.new_table(
            self.url, self.pr_key, self.token, name=table, columns=columns)
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)
        # create new contract for insert data in user table
        contr = tools.read_fixtures_yaml('simvolio')
        cont = contr['DBFindSortedUserTable']
        tx_cont = contract.new_contract(
            self.url, self.pr_key, self.token, source=str(cont['code']))
        check.is_tx_in_block(self.url, self.wait, tx_cont, self.token)
        # call contract, which insert data in user table
        data = {"TableName": table}
        res = actions.call_contract(
            self.url, self.pr_key, tx_cont['name'], data, self.token)
        actions.tx_status(self.url, self.wait, res, self.token)['result']
        # create page with content
        page_value = 'DBFind("{}").Columns("id,name").Limit(250)'.format(table)
        _, page_name = self.check_page(page_value)
        # get data from db
        db_res = db.get_all_sorted_records_from_table(self.db1, table)
        # get hash from data
        expected_hash = tools.get_hash_sha256(str(db_res))
        # test
        expected_list = {}
        actual_list = {}
        i = 0
        while i < 10:
            expected_list[i] = expected_hash
            # get content from page
            content = actions.get_content(
                self.url, 'page', page_name, '', 1, self.token)
            dbfind_list = []
            dbfind_data = content['tree'][0]['attr']['data']
            for el in dbfind_data:
                id = int(el[0])
                name = el[1]
                t = (id, name)
                dbfind_list.append(t)
            actual_hash = tools.get_hash_sha256(str(dbfind_list))
            actual_list[i] = actual_hash
            i += 1
        self.uni.assertDictEqual(expected_list, actual_list, 'Hashes is not equals')
