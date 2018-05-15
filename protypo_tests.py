import unittest
import utils
import config
import requests
import json
import time
import funcs
import datetime
import os


class PrototipoTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.getNodeConfig()
        global url, prKey, token, dbHost, dbName, login, password
        self.pages = config.readFixtures("pages")
        url = self.config["2"]["url"]
        prKey = self.config["1"]['private_key']
        self.data = utils.login(url,prKey)
        token = self.data["jwtToken"]
        dbHost = self.config["2"]["dbHost"]
        dbName = self.config["2"]["dbName"]
        login = self.config["2"]["login"]
        password = self.config["2"]["pass"]

    def assertTxInBlock(self, result, jwtToken):
        self.assertIn("hash",  result)
        status = utils.txstatus(url,
                                self.config["1"]["time_wait_tx_in_block"],
                                result['hash'], jwtToken)
        self.assertNotIn(json.dumps(status), 'errmsg')
        self.assertGreater(len(status['blockid']), 0)

    def check_page(self, sourse):
        name = "Page_" + utils.generate_random_name()
        data = {"Name": name, "Value": sourse, "ApplicationId": 1,
                "Conditions": "true", "Menu": "default_menu"}
        resp = utils.call_contract(url, prKey, "NewPage", data, token)
        self.assertTxInBlock(resp, token)
        cont = funcs.get_content(url, "page", name, "", 1, token)
        return cont

    def findPositionElementInTree(self, contentTree, tagName):
        i = 0
        while i < len(contentTree):
            if contentTree[i]['tag'] == tagName:
                return i
            i += 1

    def findPositionElementInTreeByAttributeNameAndValue(self, contentTree, tagName, attrName, attrValue):
        i = 0
        while i < len(contentTree):
            if contentTree[i]['tag'] == tagName:
                if contentTree[i]['attr'][attrName] == attrValue:
                    return i
            i += 1

    def check_post_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_post_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
        return result

    def check_get_api(self, endPoint, data, keys):
        end = url + endPoint
        result = funcs.call_get_api(end, data, token)
        for key in keys:
            self.assertIn(key, result)
        return result
        
    def test_page_button(self):
        contract = self.pages["button"]
        content = self.check_page(contract["code"])
        self.assertEqual(content["tree"][0]["tag"], "button",
                         "There is no button in content" + str(content["tree"]))

    def test_page_button_composite_contract(self):
        contract = self.pages["buttonCompositeContract"]
        content = self.check_page(contract["code"])
        partContent = content["tree"]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent[0]["tag"],
                      compositeName=partContent[0]["attr"]["composite"][0]["name"],
                      compositeData=partContent[0]["attr"]["composite"][0]["data"][0],
                      text=partContent[0]["children"][0]["text"])
        page = dict(tag=contractContent[0]["tag"],
                    compositeName=contractContent[0]["attr"]["composite"][0]["name"],
                    compositeData=contractContent[0]["attr"]["composite"][0]["data"][0],
                    text=contractContent[0]["children"][0]["text"])
        self.assertDictEqual(mustBe, page, "now has problem: " + str(content["tree"]))
        
    def test_page_selectorFromDB(self):
        contract = self.pages["selectorFromDB"]
        content = self.check_page(contract["code"])
        requiredTagNum = self.findPositionElementInTree(content["tree"],"dbfind")
        mustBe = dict(tag = "dbfind", data = True)
        page = dict(tag = content["tree"][requiredTagNum]["tag"], data = len(content["tree"][requiredTagNum]["attr"]["columns"]) > 2)
        self.assertDictEqual(mustBe, page,
                         "DBfind has problem: " + str(content["tree"]))
        
    def test_page_selectorFromData(self):
        contract = self.pages["selectorFromData"]
        content = self.check_page(contract["code"])
        mustBe = dict(tag = "data", columns = ['gender'], source = "myData",
                      select = "select", selectName = "mySelect", selectSourse = "myData")
        page = dict(tag = content["tree"][0]["tag"], columns = content["tree"][0]["attr"]["columns"],
                    source = content["tree"][0]["attr"]["source"],
                    select = content["tree"][2]["tag"], selectName = content["tree"][2]["attr"]["name"],
                    selectSourse = content["tree"][2]["attr"]["source"])
        self.assertDictEqual(mustBe, page,
                         "selectorFromData has problem: " + str(content["tree"]))
        
    def test_page_now(self):
        contract = self.pages["now"]
        content = self.check_page(contract["code"])
        contractContent = contract["content"]
        partContent = content['tree'][0]
        mustBe = dict(tagOwner=contractContent["tag"],
                      tag=contractContent["children"][0]["tag"],
                      format=contractContent["children"][0]["attr"]["format"],
                      interval=contractContent["children"][0]["attr"]["interval"])
        page = dict(tagOwner=partContent["tag"],
                      tag=partContent["children"][0]["tag"],
                      format=partContent["children"][0]["attr"]["format"],
                      interval=partContent["children"][0]["attr"]["interval"])
        self.assertDictEqual(mustBe, page, "now has problem: " + str(content["tree"]))
        
    def test_page_divs(self):
        contract = self.pages["divs"]
        content = self.check_page(contract["code"])
        # outer DIV
        partContent = content['tree'][0]
        # first level inner DIV
        requiredInnerTagNum = self.findPositionElementInTree(content['tree'][0]['children'], "div")
        partContent1 = content['tree'][0]['children'][requiredInnerTagNum]
        contractContent1 = contract["content"]['children']
        # second level inner DIV
        requiredInner2TagNum = self.findPositionElementInTree(
            content['tree'][0]['children'][requiredInnerTagNum]['children'], "div")
        partContent2 = content['tree'][0]['children'][requiredInnerTagNum]['children'][requiredInner2TagNum]
        contractContent2 = contract["content"]['children']['children']
        mustBe = dict(firstDivTag=partContent['tag'],
                      firstDivClass=partContent['attr']['class'],
                      innerDivTag1=partContent1['tag'],
                      innerDivClass1=partContent1['attr']['class'],
                      innerDivTag2=partContent2['tag'],
                      innerDivClass2=partContent2['attr']['class'],
                      childrenText=partContent2['children'][0]['text'])
        page = dict(firstDivTag=contract["content"]['tag'],
                    firstDivClass=contract["content"]['attr']['class'],
                    innerDivTag1=contractContent1['tag'],
                    innerDivClass1=contractContent1['attr']['class'],
                    innerDivTag2=contractContent2['tag'],
                    innerDivClass2=contractContent2['attr']['class'],
                    childrenText=contractContent2['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "divs has problem: " + str(content["tree"]))

    def test_page_setVar(self):
        contract = self.pages["setVar"]
        content = self.check_page(contract["code"])
        requiredTagNum = self.findPositionElementInTree(content['tree'], "div")
        partContent = content['tree'][requiredTagNum]
        contractContent = contract['content']
        mustBe = dict(tag=partContent['tag'],
                    childrenText=partContent['children'][0]['text'])
        page = dict(tag=contractContent['tag'],
                    childrenText=contractContent['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "setVar has problem: " + str(content["tree"]))

    def test_page_input(self):
        contract = self.pages["input"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      inputClass=partContent['attr']['class'],
                      name=partContent['attr']['name'],
                      placeholder=partContent['attr']['placeholder'],
                      type=partContent['attr']['type'])
        page = dict(tag=contractContent['tag'],
                    inputClass=contractContent['attr']['class'],
                    name=contractContent['attr']['name'],
                    placeholder=contractContent['attr']['placeholder'],
                    type=contractContent['attr']['type'])
        self.assertDictEqual(mustBe, page,
                             "input has problem: " + str(content["tree"]))
        
    def test_page_menuGroup(self):
        contract = self.pages["menuGroup"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        menuItem1 = contractContent['children'][0]
        menuItem2 = contractContent['children'][1]
        requiredNumMenuItem1 = self.findPositionElementInTreeByAttributeNameAndValue(partContent['children'],
                                                                "menuitem", "title", menuItem1['attr']['title'])
        requiredNumMenuItem2 = self.findPositionElementInTreeByAttributeNameAndValue(partContent['children'],
                                                                "menuitem", "title", menuItem2['attr']['title'])
        partContent1 = partContent['children'][requiredNumMenuItem1]
        partContent2 = partContent['children'][requiredNumMenuItem2]
        mustBe = dict(menuTag=partContent['tag'],
                      name=partContent['attr']['name'],
                      title=partContent['attr']['title'],
                      menuItemTag1=partContent1['tag'],
                      menuItemPage1=partContent1['attr']['page'],
                      menuItemTitle1=partContent1['attr']['title'],
                      menuItemTag2=partContent2['tag'],
                      menuItemPage2=partContent2['attr']['page'],
                      menuItemTitle2=partContent2['attr']['title'])
        page = dict(menuTag=contractContent['tag'],
                    name=contractContent['attr']['name'],
                    title=contractContent['attr']['title'],
                    menuItemTag1 = partContent1['tag'],
                    menuItemPage1 = menuItem1['attr']['page'],
                    menuItemTitle1 = menuItem1['attr']['title'],
                    menuItemTag2=partContent2['tag'],
                    menuItemPage2=menuItem2['attr']['page'],
                    menuItemTitle2=menuItem2['attr']['title'])
        self.assertDictEqual(mustBe, page,
                             "menuGroup has problem: " + str(content["tree"]))

    def test_page_linkPage(self):
        contract = self.pages["linkPage"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      linkPageClass=partContent['attr']['class'],
                      page=partContent['attr']['page'],
                      text=partContent['children'][0]['text'])
        page = dict(tag=contractContent['tag'],
                      linkPageClass=contractContent['attr']['class'],
                      page=contractContent['attr']['page'],
                      text=contractContent['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "linkPage has problem: " + str(content["tree"]))

    def test_page_ecosysParam(self):
        contract = self.pages["ecosysParam"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "ecosysParam has problem: " + str(content["tree"]))
        
    def test_page_paragraph(self):
        contract = self.pages["paragraph"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['text'])
        self.assertDictEqual(mustBe, page,
                             "paragraph has problem: " + str(content["tree"]))

    def test_page_getVar(self):
        contract = self.pages["getVar"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "getVar has problem: " + str(content["tree"]))

    def test_page_iff(self):
        contract = self.pages["iff"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['text'])
        self.assertDictEqual(mustBe, page,
                             "iff has problem: " + str(content["tree"]))
        
    def test_page_orr(self):
        contract = self.pages["orr"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['text'])
        self.assertDictEqual(mustBe, page,
                             "orr has problem: " + str(content["tree"]))
        
    def test_page_andd(self):
        contract = self.pages["andd"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['text'])
        self.assertDictEqual(mustBe, page,
                             "andd has problem: " + str(content["tree"]))
        
    def test_page_form(self):
        contract = self.pages["form"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        partContent1 = content['tree'][0]['children'][0]['children'][0]
        contractContent = contract["content"]
        contractContent1 = contract["content"]['children'][0]['children'][0]
        mustBe = dict(formTag=partContent['tag'],
                      spanTag=partContent['children'][0]['tag'],
                      spanText = partContent1['text'])
        page = dict(formTag=contractContent['tag'],
                    spanTag=contractContent['children'][0]['tag'],
                    spanText = contractContent1['text'])
        self.assertDictEqual(mustBe, page,
                             "form has problem: " + str(content["tree"]))
        
    def test_page_label(self):
        contract = self.pages["label"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      labelFor=partContent['attr']['for'])
        page = dict(tag=contractContent['tag'],
                      labelFor=contractContent['attr']['for'])
        self.assertDictEqual(mustBe, page,
                             "label has problem: " + str(content["tree"]))
        
    def test_page_span(self):
        contract = self.pages["span"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]['text'])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]['text'])
        self.assertDictEqual(mustBe, page,
                             "span has problem: " + str(content["tree"]))
        
    def test_page_langRes(self):
        lang = "lang_"+utils.generate_random_name()
        data = {"ApplicationId": 1,
                "Name": lang,
                "Trans": "{\"en\": \"Lang_en\", \"ru\" : \"Язык\", \"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = utils.call_contract(url, prKey, "NewLang", data, token)
        self.assertTxInBlock(res, token)
        world = "world_" + utils.generate_random_name()
        data = {"ApplicationId": 1,
                "Name": world,
                "Trans": "{\"en\": \"World_en\", \"ru\" : \"Мир_ru\", \"fr-FR\": \"Monde_fr-FR\", \"de\": \"Welt_de\"}"}
        res = utils.call_contract(url, prKey, "NewLang", data, token)
        self.assertTxInBlock(res, token)
        contract = self.pages["langRes"]
        content = self.check_page("LangRes("+lang+") LangRes("+world+", ru)")
    
        
    def test_page_inputErr(self):
        contract = self.pages["inputErr"]
        content = self.check_page(contract["code"])
        # iterating response elements
        requiredTagNum = self.findPositionElementInTree(content['tree'],"inputerr")
        partContent = content['tree'][requiredTagNum]['tag']
        self.assertEqual(partContent, contract["content"]['tag'],
                         "Error in content " + str(content['tree']))
        partContent = content['tree'][requiredTagNum]['attr']
        contractContent = contract["content"]['attr']
        mustBe = dict(maxlength=partContent['maxlength'],
                      name=partContent['name'],
                      minlength=partContent['minlength'])
        page = dict(maxlength=contractContent['maxlength'],
                      name=contractContent['name'],
                      minlength=contractContent['minlength'])
        self.assertDictEqual(mustBe, page,
                             "inputErr has problem: " + str(content["tree"]))

    def test_page_include(self):
        name = "Block_"+utils.generate_random_name()
        data = {"Name": name, "ApplicationId": 1,
                "Value": "Hello page!", "Conditions": "true"}
        res = utils.call_contract(url, prKey, "NewBlock", data, token)
        self.assertTxInBlock(res, token)
        contract = self.pages["include"]
        content = self.check_page("Include("+name+")")
        self.assertEqual(content["tree"][0]["text"], contract["content"][0]["text"],
                         "include has problem: " + str(content["tree"]))
        
    def test_page_inputImage(self):
        contract = self.pages["inputImage"]
        content = self.check_page(contract["code"])
        partContent = content["tree"][0]
        contractContent = contract["content"][0]
        mustBe = dict(tag=partContent["tag"],
                      name=partContent["attr"]["name"],
                      ratio=partContent["attr"]["ratio"],
                      width=partContent["attr"]["width"])
        page = dict(tag=contractContent["tag"],
                    name=contractContent["attr"]["name"],
                    ratio=contractContent["attr"]["ratio"],
                    width=contractContent["attr"]["width"])
        self.assertDictEqual(mustBe, page,
                             "inputErr has problem: " + str(content["tree"]))
        
    def test_page_alert(self):
        contract = self.pages["alert"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        partContent1 = content['tree'][0]['attr']['alert']
        contractContent1 = contract["content"]['attr']['alert']
        mustBe = dict(tag=partContent["tag"],
                      cancelbutton = partContent1['cancelbutton'],
                      confirmbutton = partContent1['confirmbutton'],
                      icon = partContent1['icon'],
                      text = partContent1['text'])
        page = dict(tag=contractContent["tag"],
                    cancelbutton=contractContent1['cancelbutton'],
                    confirmbutton=contractContent1['confirmbutton'],
                    icon=contractContent1['icon'],
                    text=contractContent1['text'])
        self.assertDictEqual(mustBe, page,
                             "alert has problem: " + str(content["tree"]))
        
    def test_page_table(self):
        contract = self.pages["table"]
        content = self.check_page(contract["code"])
        mustBe = dict(tag = "dbfind", source = "mysrc",
                      tag2 = "table", columns = [{'Name': 'name', 'Title': 'Name'}, {'Name': 'value', 'Title': 'Value'}, {'Name': 'conditions', 'Title': 'Conditions'}])
        page = dict(tag = content["tree"][0]["tag"], source = content["tree"][1]["attr"]["source"],
                    tag2 = content["tree"][1]["tag"],
                    columns = content["tree"][1]["attr"]["columns"])
        self.assertDictEqual(mustBe, page,
                         "selectorFromData has problem: " + str(content["tree"]))
        
    def test_page_kurs(self):
        contract = self.pages["kurs"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"][0]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]["text"])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "kurs has problem: " + str(content["tree"]))

    def test_page_strong(self):
        contract = self.pages["strong"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"][0]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]["text"])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "strong has problem: " + str(content["tree"]))

    def test_page_getColumnType(self):
        contract = self.pages["getColumnType"]
        content = self.check_page(contract["code"])
        self.assertEqual(str(content["tree"][0]["text"]), contract["content"]["text"],
                         "getColumnType has problem: " + str(content["tree"]))
        
    def test_page_sys_var_isMobile(self):
        contract = self.pages["sys_var_isMobile"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"][0]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]["text"])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "isMobile has problem: " + str(content["tree"]))

    def test_page_sys_var_roleID(self):
        contract = self.pages["sys_var_roleID"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"][0]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]["text"])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "roleID has problem: " + str(content["tree"]))

    def test_page_sys_var_ecosystemID(self):
        contract = self.pages["sys_var_ecosystemID"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"][0]
        mustBe = dict(tag=partContent['tag'],
                      text=partContent['children'][0]["text"])
        page = dict(tag=contractContent['tag'],
                    text=contractContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "ecosystemID has problem: " + str(content["tree"]))

    def test_page_sys_var_ecosystem_name(self):
        # get ecosystem name from api
        asserts = ["list"]
        res = self.check_get_api("/list/ecosystems", "", asserts)
        id = 1
        i = 0
        requiredEcosysName = ""
        while i < int(res['count']):
            if int(res['list'][i]['id']) == id:
                requiredEcosysName = res['list'][i]['name']
            i += 1
        #test
        contract = self.pages["sys_var_ecosystem_name"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        mustBe = dict(tag="em",
                      text=requiredEcosysName)
        page = dict(tag=partContent['tag'],
                    text=partContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "ecosystem_name has problem: " + str(content["tree"]))

    def test_page_sys_var_key_id(self):
        content = self.check_page("Em(EcosysParam(founder_account))")
        founderAcc = content["tree"][0]["children"][0]["text"]
        contract = self.pages["sys_var_keyID"]
        content = self.check_page(contract["code"])
        keyID=content["tree"][0]["children"][0]["text"]
        self.assertEqual(keyID, founderAcc,
                        "key_id has problem: " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_dbfind_count(self):
        asserts = ["count"]
        data = {}
        res = self.check_get_api("/contracts", data, asserts)
        contractsCount = res["count"]
        contract = self.pages["dbfindCount"]
        content = self.check_page(contract["code"])
        RequiredNum = self.findPositionElementInTree(content["tree"],"em")
        page = content['tree'][RequiredNum]["children"][0]["text"]
        self.assertEqual(contractsCount, page,
                        "dbfind_count has problem: " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_dbfind_where_count(self):
        contract = self.pages["dbfindWhereCount"]
        content = self.check_page(contract["code"])
        RequiredNum = self.findPositionElementInTree(content["tree"],"em")
        page = content['tree'][RequiredNum]["children"][0]["text"]
        self.assertEqual(contract["content"], page,
                        "dbfind_where_count has problem: " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_dbfind_whereId_count(self):
        contract = self.pages["dbfindWhereIdCount"]
        content = self.check_page(contract["code"])
        RequiredNum = self.findPositionElementInTree(content["tree"],"em")
        page = content['tree'][RequiredNum]["children"][0]["text"]
        self.assertEqual(contract["content"], page,
                        "dbfind_whereId_count has problem: " + contract["content"] + ". Content = " + str(content["tree"]))

    def test_binary(self):
        # this test has not fixture
        name = "image_" + utils.generate_random_name()
        appID = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": appID}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        self.assertTxInBlock(resp, token)
        self.assertIn("hash", str(resp), "BlockId is not generated: " + str(resp))
        # test
        MemberID = utils.getFounderId(dbHost, dbName, login, password)
        lastRec = funcs.get_count(url, "binaries", token)
        content = self.check_page("Binary(Name: "+name+", AppID: "+appID+", MemberID: "+MemberID+")")
        msg = "test_binary has problem. Content = " + str(content["tree"])
        self.assertEqual("/data/1_binaries/"+lastRec+"/data/b40ad01eacc0312f6dd1ff2a705756ec", content["tree"][0]["text"])

    def test_binary_by_id(self):
        # this test has not fixture
        name = "image_" + utils.generate_random_name()
        appID = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": appID}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        res = self.assertTxInBlock(resp, token)
        self.assertIn("hash", str(resp), "BlockId is not generated: " + str(resp))
        # test
        lastRec = funcs.get_count(url, "binaries", token)
        content = self.check_page("Binary().ById("+lastRec+")")
        msg = "test_binary has problem. Content = " + str(content["tree"])
        self.assertEqual("/data/1_binaries/"+lastRec+"/data/b40ad01eacc0312f6dd1ff2a705756ec", content["tree"][0]["text"])

    def test_image_binary(self):
        # this test has not fixture
        name = "image_" + utils.generate_random_name()
        appID = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": appID}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        self.assertTxInBlock(resp, token)
        self.assertIn("hash", str(resp), "BlockId is not generated: " + str(resp))
        # test
        MemberID = utils.getFounderId(dbHost, dbName, login, password)
        lastRec = funcs.get_count(url, "binaries", token)
        content = self.check_page("Image(Binary(Name: "+name+", AppID: "+appID+", MemberID: "+MemberID+"))")
        partContent = content["tree"][0]
        mustBe = dict(tag=partContent['tag'],
                      src=partContent['attr']["src"])
        page = dict(tag="image",
                    src="/data/1_binaries/"+lastRec+"/data/b40ad01eacc0312f6dd1ff2a705756ec")
        self.assertDictEqual(mustBe, page,
                             "test_image_binary has problem: " + str(content["tree"]))

    def test_image_binary_by_id(self):
        # this test has not fixture
        name = "image_" + utils.generate_random_name()
        appID = "1"
        path = os.path.join(os.getcwd(), "fixtures", "image2.jpg")
        with open(path, 'rb') as f:
            file = f.read()
        files = {'Data': file}
        data = {"Name": name, "ApplicationId": appID}
        resp = utils.call_contract_with_files(url, prKey, "UploadBinary", data,
                                              files, token)
        self.assertTxInBlock(resp, token)
        self.assertIn("hash", str(resp), "BlockId is not generated: " + str(resp))
        # test
        lastRec = funcs.get_count(url, "binaries", token)
        content = self.check_page("Image(Binary().ById("+lastRec+"))")
        partContent = content["tree"][0]
        mustBe = dict(tag=partContent['tag'],
                      src=partContent['attr']["src"])
        page = dict(tag="image",
                    src="/data/1_binaries/"+lastRec+"/data/b40ad01eacc0312f6dd1ff2a705756ec")
        self.assertDictEqual(mustBe, page,
                             "test_image_binary_by_id has problem: " + str(content["tree"]))
        
    def test_address(self):
        contract = self.pages["address"]
        content = self.check_page(contract["code"])
        partContent = content['tree'][0]
        contractContent = contract["content"]
        mustBe = dict(tagOwner=contractContent['tag'],
                      tag=contractContent['children'][0]["tag"],
                      text=contractContent['children'][0]["text"])
        page = dict(tagOwner=partContent['tag'],
                    tag=partContent['children'][0]["tag"],
                    text=partContent['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "address has problem: " + str(content["tree"]))

    def test_money(self):
        contract = self.pages["money"]
        content1 = self.check_page(contract["code1"])
        content2 = self.check_page(contract["code2"])
        partContent1 = content1['tree'][0]
        partContent2 = content2['tree'][0]
        contractContent1 = contract["content1"]
        contractContent2 = contract["content2"]
        mustBe = dict(tagOwner1=contractContent1['tag'],
                      tag1=contractContent1['children'][0]["tag"],
                      text1=contractContent1['children'][0]["text"],
                      tagOwner2 = contractContent2['tag'],
                      tag2 = contractContent2['children'][0]["tag"],
                      text2 = contractContent2['children'][0]["text"])
        page = dict(tagOwner1=partContent1['tag'],
                    tag1=partContent1['children'][0]["tag"],
                    text1=partContent1['children'][0]["text"],
                    tagOwner2=partContent2['tag'],
                    tag2=partContent2['children'][0]["tag"],
                    text2=partContent2['children'][0]["text"])
        self.assertDictEqual(mustBe, page,
                             "money has problem: " + "\n" + str(content1["tree"]) + "\n" + str(content2["tree"]))

    def test_calculate(self):
        contract = self.pages["calculate"]
        content1 = self.check_page(contract["code1"])
        content2 = self.check_page(contract["code2"])
        content3 = self.check_page(contract["code3"])
        content4 = self.check_page(contract["code4"])
        content5 = self.check_page(contract["code5"])
        partContent1 = content1['tree'][0]
        partContent2 = content2['tree'][0]
        partContent3 = content3['tree'][0]
        partContent4 = content4['tree'][0]
        partContent5 = content5['tree'][0]
        contractContent1 = contract["content1"]
        contractContent2 = contract["content2"]
        contractContent3 = contract["content3"]
        contractContent4 = contract["content4"]
        contractContent5 = contract["content5"]
        print(partContent1)
        print(partContent2)
        print(partContent3)
        print(partContent4)
        print(partContent5)


if __name__ == '__main__':
    unittest.main()
