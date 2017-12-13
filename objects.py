class Pages(object):
    button = ("button_page", "Button(Body: Create user, Class: btn btn-primary, Contract: NewUser)","default_menu")
    selectorFromDB = ("selector_fromData_page", "DBFind(\"pages\", data) %n Select(MySelect, data, \"name\")","default_menu")
    selectorFromData = ("selector_from", "Data(myData, \"gender\"){\"Men\", \"Women\", \"Between\"} %n Select(mySelect, myData, \"gender\")","default_menu")
    now = ("now_page", "P(Today is Now(DD.MM.YYYY)) %n P(In Moskow now: Now(datetime,-3 hours))","default_menu")
    divs = ("divs_page", "Div(content-wrapper){ %n Div(panel panel-primary){ %n Div(panel-heading, Header) %n }}","default_menu")
    setVar = ("set_var_page", "SetVar(head, Header) Div(panel-heading, #head#)","default_menu")
    input = ("input_page", "Input(Class: form-control, Placeholder: text, Type: text, Name: name)","default_menu")
    menuGroup = ("menu_group_page", "MenuGroup(My Menu){ MenuItem(Dahsboard, dashboard_default) MenuItem(Main, default_page)}","default_menu")
    linkPage = ("link_page", "LinkPage(Show my wallet, default_page, mybtn_class)","default_menu")
    ecosysParam = ("ecosys_param_page", "Span(Address(EcosysParam(founder_account)))","default_menu")
    paragraf = ("paragraf_page", "p(This is paragraph)","default_menu")
    getVar = ("get_var_page", "SetVar(name, FullName) Span(GetVar(name))","default_menu")
    iff = ("if_page", "If(1<5){5 bigger than 1}.Else{Error}","default_menu")
    orr = ("or_page", "If(Or(1>5,10>5), 1 or 10 bigger than 5)","default_menu")
    andd = ("and_page", "If(And(1>0,5>0), 1 and 5 bigger than 0)","default_menu")
    form = ("form_page", "Form(){Span(Test)}","default_menu")
    label = ("label_page", "Label(For: name)","default_menu")
    span = ("span_page", "Span(Test)","default_menu")
    langRes = ("lang_res_page", "LangRes(lang) LangRes(word, ru)","default_menu")
    inputErr = ("input_err_page", "InputErr(Name: Login, minLength: Value is too short, maxLength: The length of the value must be less than 10 characters)Input(Name: Login, Type: text).Validate(minLength: 6, maxLength: 10)","default_menu")
    include = ("include_page", "Include(Block1)","default_menu")
    image = ("image_page", "Image(avatar)","default_menu")
    inputImage = ("input_image_page", "ImageInput(avatar, 100, 2/1)","default_menu")
    allert = ("allert_page", "Button(Body: Create user, Class: btn btn-primary, Contract: NewUser).Alert(Text: Name, ConfirmButton: Ok, CancelButton: Cancel, Icon: question)", "default_menu")
    table = ("table_page", "DBFind(\"blocks\",mysrc) Table(mysrc,\"Name=name,Value=value,Conditions=conditions\")","default_menu")
    kurs = ("kurs_page", "This is an Em(cursive)", "default_menu")
    strong = ("strong_page", "This is an Strong(strong)", "default_menu")
    
class Contracts(object):
    updSysParam = ("""{
    data {
    }
    conditions {
    }
    action {
        var par map
        par["Name"] = "number_of_nodes"
        par["Value"] = "13"
        CallContract("UpdateSysParam", "")
    }
    }""", "")
    dbFind = (""" {
    data {}
    conditions {}
    action {
        var res array
        var val map
        res = DBFind("pages").Columns("name").Where("id=?", 1).Order("id")
        val = res[0]
        $result = val["name"]
    }
    }""", "default")
    ecosysParam = ("""{
    data {}
    conditions {}
    action {
        var res string
        res = EcosysParam("changing_menu")
        $result=res
    }
    }""", "MainCondition")
    #needs to add record to history table
    ifMap = ("""{
    data {
    }
    conditions {
    }
    action {
        var my map
        my["test"] = 1
        if my {
            $result="true"
        }
        else {
            $result="false"
        }
    }
    }""", "true")
    dbRow = ("""{
    data {
    }
    conditions {
    }
    action {
        var vals map
        vals = DBRow("pages").Columns("name, menu").Where("id = ?", 1)
        $result=vals["name"]
    }
    }""", "default_page")
    dbFreeRequest = ()
    #needs to create language resourse with name - test and localisacions:en- test_en, de- test_de
    langRes = ("""{
    data {
    }
    conditions {
    }
    action {
        $result=LangRes("test", "de")
    }
    }""", "test_de")
    #needs to create table "test" with "name" and "test" string columns
    dbInsert = ("""{
    data {
    }
    conditions {
    }
    action {
        $result=DBInsert("tests", "name,test", "name", "val")
    }
    }""","1")
    #needs to create table "reports_test" with "name" and "test" string columns
    #needs to create table "test2" with "name" and "case" string columns and to add 1 record there
    dbUpdate = ("""{
    data {
    }
    conditions {
    }
    action {
        $result=DBUpdate("test2", 1, "name,case", "test_edited", "case_edited")
    }
    }""", "1")
    #needs to create table "test3" with "name" and "case" string columns and to add 1 record with name=myTest
    dbUpdateExt = ("""{
    data {
    }
    conditions {
    }
    action {
        $result=DBUpdateExt("test3", "name", "myTest", "name,case", "mytest_edited", "myCase_edited")
    }
    }""", "1")
    #needs to ctreate ecosystem with name "MyEcosystem"
    findEcosystem = ("""{
    data {
    }
    conditions {
    }
    action {
        $result=FindEcosystem(`MyEcosystem`)
    }
    }""", "2")
    #needs to create Contarct "MyContract"
    callContract = ("""{
    data {
    }
    conditions {
    }
    action {
        CallContract("MyContract", "")
    }
    }""", "")
    #needs to create contract "AccesContr"
    contractAccess = ("""{
    data {
    }
    conditions {
    }
    action {
        ContractAccess("AccesContr")
    }
    }""", "")
    contractConditions = ()
    evalCondition = ("""{
    data {
    }
    conditions {
    }
    action {
        EvalCondition("pages", "default_page", `conditions`)
    }
    }""", "")
    validateCondition = ("""{
    data {
    }
    conditions {
    }
    action {
        ValidateCondition("ContractConditions(`MainCondition`)", 0)
    }
    }""", "")
    addressToId = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = AddressToId("0005-2070-2000-0006-0200")
    }
    }""","52070200000060200")
    contains =("""{
    data {
    }
    conditions {
    }
    action {
        if Contains("Hello world", `Hello`) {
            $result = "Hello world"
        }
    }
    }""", "Hello world")
    float = ("""{
    data {
    }
    conditions {
    }
    action {
        var val int
        val = Float("567") + Float(232)
            $result = Str(val)
    }
    }""", "799.000000")
    hasPrefix = ("""{
    data {
    }
    conditions {
    }
    action {
        if HasPrefix("myString", `my`) {
            $result = "Prefix"
        }
    }
    }""", "Prefix")
    hexToBytes = ("""{
    data {
    }
    conditions {
    }
    action {
            $result = Str(HexToBytes("34fe4501a4d80094"))
    }
    }""", "[52 254 69 1 164 216 0 148]")
    Int = ("""{
    data {
    }
    conditions {
    }
    action {
        var val int
        val = Int("105") + Int("45")
            $result = Str(val)
    }
    }""", "150")
    len = ("""{
    data {
    }
    conditions {
    }
    action {
        var arr array
        arr[0] = "1"
        arr[1] = "2"
        arr[2] = "3"
        $result = Len(arr)
    }
    }""", "3")
    pubToID = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = PubToID("05f1521f6a7e769ebbde2ab3df01f4740d1408e7e7150745cac9fb953d8ad366")
    }
    }""", "-6799051354910978041")
    replace = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = Replace("this is my decision, this is my gole, this is my life", `this is my`, `your`)
    }
    }""", "your decision, your gole, your life")
    size = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = Size("hello")
    }
    }""", "5")
    sha256 = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = Sha256("Test")
    }
    }""", "532eaabd9574880dbf76b9b8cc00832c20a6ec113d682299550d7a6e0f345e25")
    Sprintf =("""{
    data {
    }
    conditions {
    }
    action {
        $result = Sprintf("%s is %d", "Five", 5)
    }
    }""", "Five is 5")
    str = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = Str(5.678)
    }
    }""", "5.678")
    substr = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = Substr("ecosystema", 2, 5)
    }
    }""", "osyst")
    updateLang = ("""{
    data {
    }
    conditions {
    }
    action {
        UpdateLang("test", "{'ru': 'Тест'}")
    }
    }""","")
    sysParamString = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = SysParamString("blockchain_url")
    }
    }""", "")
    sysParamInt  = ("""{
    data {
    }
    conditions {
    }
    action {
        $result = Str(SysParamInt("max_columns"))
    }
    }""", "50")
    sysCost = ()
    updateSysParam =()
class Blocks(object):
    superBlock = ("test_block", "My supper block")
    

