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
    dbFind = (""" {
    data {}
    conditions {}
    action {
        var res array
        res = DBFind("blocks").Columns("id,value").Where("id=?", 1).Order("id")
        $result = "i returned"
    }
    }""", "i")
    
    dbAmount = ()
    ecosysParam = ()
    dbIntExt = ()
    dbIntWhere = ()
    dbRowExt = ()
    dbString = ()
    dbStringExt = ()
    dbFreeRequest = ()
    dbStringWhere = ()
    langRes = ()
    dbInsert = ()
    dbInsertReport = ()
    dbUpdate = ()
    dbUpdateExt = ()
    findEcosystem = ()
    callContract = ()
    contractConditions = ()
    evalCondition = ()
    validateCondition = ()
    addressToId = ()
    contains =()
    float = ()
    hasPrefix = ()
    hexToBytes = ()
    Int = ()
    len = ()
    pubToID = ()
class Blocks(object):
    superBlock = ("test_block", "My supper block")
    

