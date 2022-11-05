import sys
from utils import *


def checker(self,domain, problem):

    domain_name = domain
    problem_name = problem
    #-----------------------------
    problem_without_comment = "examples-pddl/without_comment/problem_without_comment.pddl"
    domain_without_comment = "examples-pddl/without_comment/domain_without_comment.pddl"

    #*********************************** DOMAIN CHECKS***********************************
    c_open = 0
    c_close = 0
    source_path = domain_name
    problem_path = domain_without_comment
    delete_comments(self,source_path,problem_path)
    file_replace_word(self,problem_path,problem_path ,"(define"   ,"(define ")
    file_replace_word(self,problem_path,problem_path ,"(domain"   ,"(domain ")
    file_replace_word(self,problem_path,problem_path ,"(:predicates"   ,"(:predicates ")
    file_replace_word(self,problem_path,problem_path ,":parameters"   ,":parameters ")
    file_replace_word(self,problem_path,problem_path ,":precondition"   ,":precondition ")
    file_replace_word(self,problem_path,problem_path ,":effect"   ,":effect ")
    file_replace_word(self,problem_path,problem_path ,"(:objects"   ,"(:objects ")


    #CHECK BRACKETS

    if (self.print_checker == 0):
        self.textBrowser.append("\nCHECKS ON: " + problem_path)
        self.textBrowser.append("\nPRELIMINARY CHECKS\n")

    c_open = elem_counter(self,problem_path,'(',"no")
    c_close = elem_counter(self,problem_path,')',"no")
    if((c_open == c_close) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Number of ( , ) is " + str(c_open) )
    else:
        if((c_open>c_close) and (self.print_checker == 0)):
            self.textBrowser.append("[ \u2718 ][ERROR-11] You put more ( than " + str(c_open-c_close)  )
            self.error_function(1)
            self.textBrowser.append("In line " + str(parenthesis_index(self,problem_path,"OPENED","(",")")) )
        elif (self.print_checker == 0):
            self.textBrowser.append("[ \u2718 ][ERROR-12] You put more ) than " + str(c_close-c_open)  )
            self.error_function(1)
            self.textBrowser.append("In line " + str(parenthesis_index(self,problem_path,"CLOSED","(",")")) )
    c_open = elem_counter(self,problem_path,'[',"no")
    c_close = elem_counter(self,problem_path,']',"no")
    if((c_open == c_close) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Number of [ , ] is " + str(c_open) ) 
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-13] Number of \n [ = " + str(c_open) +  "\n ] = " + str(c_close) )
        self.error_function(1)

    c_open = elem_counter(self,problem_path,'{',"no")
    c_close = elem_counter(self,problem_path,'}',"no")
    if((c_open == c_close) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Number of { , } is " + str(c_open) )
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-14] Number of \n { = " + str(c_open) +  "\n } = " + str(c_close) )
        self.error_function(1)




    check_word_presence(self,"(define",problem_path,"no")
    check_word_presence(self,"(:requirements",problem_path,"no")

    check_word_presence(self,"(domain",problem_path,"no")
    check_word_presence(self,"(:predicates",problem_path,"no")
    
    predicates_dict = predicates_extracter(self,search_keyword(self,"predicates",problem_path))
    predicate_list =  predicates_dict.keys()
    if (self.print_checker == 0):
        self.textBrowser.append("[ \u2713 ] Predicates and their number of  elements: \n     "+str(predicates_dict))

    define_list =  search_keyword(self,"define",problem_path)
    domain_list = search_keyword(self,"(domain",problem_path)
    requirements_list =    search_keyword(self,"requirements",problem_path)
    predicate_list_complete =    search_keyword(self,"predicates",problem_path)

    
    types_list = search_keyword(self,"types",problem_path)

    #Number of actions
    n_actions = elem_counter(self,problem_path,"(:action","no")
    list_action_names = get_action_names(self,problem_path,n_actions)
    list_actions_Santilli = []

    counter = 0

    parameter_flag = 0

    rest_to_check = []
    effect_list_check = []
    
    for nam in list_action_names:
        list_actions_Santilli.append(list_to_string(self,search_keyword(self,"action" + str(nam),problem_path)))

        if(":parameters" in list_actions_Santilli[counter] or ":parameters(" in list_actions_Santilli[counter]):
            parameter_flag = 1
            parameters_list =  search_keyword_string(self,"parameters",list_actions_Santilli[counter])
            objects_to_check = list_to_string(self,parameters_list).replace( ")","").replace(":parameters","").replace( "(","").strip().split()
            objects_to_check = set(objects_to_check)
            init_objects_to_check = set(list_to_string(self,list_actions_Santilli[counter]).replace( ")"," ").replace(":parameters","").replace(":precondition","").replace(":effect","").replace(":action","").replace( "("," ").replace(" and ","").replace("and","").replace(" not ","").replace("not","").replace(" or ","").strip().split())
            for element in init_objects_to_check:
                if(not(element in objects_to_check)):
                    if(not(element in predicate_list)):
                        if( (not(element == '?')) and (not(element == 'or')) and (not(element == 'and')) and (not(element == 'not')) ):
                            rest_to_check.append(element)


        precondition_list =  search_keyword_string(self,"precondition",list_actions_Santilli[counter])

        if(list_to_string(self,precondition_list).replace('(','').replace(')','').replace(":precondition",'').replace('\n','').replace('\t','').replace(' ','') == ''):

            if (self.print_checker == 0):
                self.textBrowser.append("[WARNING-26] The precondition of action " + nam + " is empty")
        effect_list = search_keyword_string(self,"effect",list_actions_Santilli[counter])

        predicate_form_checker(self,precondition_list,predicate_list,"string",predicates_dict,problem_path)
        predicate_form_checker(self,effect_list,predicate_list,"string",predicates_dict,problem_path)



        #CONTROLLO RIDONDANZA EFFECT
        effect_part = list_to_string(self,effect_list).replace('\n','').replace('\t','').replace(':effect','').replace('(','').replace(')','').replace(' ','').lower()
        value = 0
        for char_elem in effect_part:
            value = value + ord(char_elem)
        effect_list_check.append(value)


        counter=counter+1


    
    counter = 0


    #CONTROLLO RIDONDANZA EFFECT
    flag_redundancy = 0

    duplicates_effect_list = []
    for int_effect in effect_list_check:
        duplicates_effect_list.append(list_duplicates_of(self,effect_list_check, int_effect))

    for idx_effects in duplicates_effect_list:
        if(len(idx_effects) > 1):
            names = ""
            for duplicat_idx in range(0,len(list_action_names)):
                if(duplicat_idx in idx_effects):
                    names = names + " " + list_action_names[duplicat_idx]
            if (self.print_checker == 0):
                self.textBrowser.append("[WARNING-4] Actions [" + names + "] have the same effects")
            flag_redundancy = 1
    if((flag_redundancy == 0) and (self.print_checker == 0)):
    	self.textBrowser.append("[ \u2713 ] There are not actions with similar effects")






    if(parameter_flag == 1):
        for action_to_remove in list_action_names:
            if(action_to_remove in rest_to_check):
                if((not(action_to_remove == 'or')) and (not(action_to_remove == 'and')) and (not(action_to_remove == 'not')) ):
                    rest_to_check.remove(action_to_remove)




    check_useless_parenthesis(self,problem_path)
    check_strange_words_domain(self,problem_path,domain_list,requirements_list,list_actions_Santilli,predicate_list_complete,types_list)
    if (self.print_checker == 0):
        self.textBrowser.append("\n-------------------------------------------------")
    




    #*********************************** PROBLEM CHECKS***********************************    

    c_open = 0
    c_close = 0
    source_path = problem_name
    problem_path = problem_without_comment
    delete_comments(self,source_path,problem_path)
    file_replace_word(self,problem_path,problem_path ,"(define"   ,"(define ")
    file_replace_word(self,problem_path,problem_path ,"(problem"  ,"(problem ")
    file_replace_word(self,problem_path,problem_path ,"(:domain"  ,"(:domain ")
    file_replace_word(self,problem_path,problem_path ,"(:objects" ,"(:objects ")
    file_replace_word(self,problem_path,problem_path ,"(:init)"   ,"(:init  )")
    file_replace_word(self,problem_path,problem_path ,"(:goal"    ,"(:goal ")
    file_replace_word(self,problem_path,problem_path ,"(:types"   ,"(:types ")






    #CHECK BRACKETS
    if (self.print_checker == 0):
        self.textBrowser.append("\nCHECKS ON: " + problem_path)
        self.textBrowser.append("\nPRELIMINARY CHECKS\n")

    c_open = elem_counter(self,problem_path,'(',"no")
    c_close = elem_counter(self,problem_path,')',"no")
    if((c_open == c_close) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Number of ( , ) is " + str(c_open) )
    else:
        if((c_open>c_close) and (self.print_checker == 0)):
            self.textBrowser.append("[ \u2718 ][ERROR-15] You put more ( than " + str(c_open-c_close)  )
            self.error_function(1)
            self.textBrowser.append("In line " + str(parenthesis_index(self,problem_path,"OPENED","(",")")) )
        elif (self.print_checker == 0):
            self.textBrowser.append("[ \u2718 ][ERROR-16] You put more ) than " + str(c_close-c_open)  )
            self.error_function(1)
            self.textBrowser.append("In line " + str(parenthesis_index(self,problem_path,"CLOSED","(",")")) )



    c_open = elem_counter(self,problem_path,'[',"no")
    c_close = elem_counter(self,problem_path,']',"no")
    if((c_open == c_close) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Number of [ , ] is " + str(c_open) ) 
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-17] Number of \n [ = " + str(c_open) +  "\n ] = " + str(c_close) )
        self.error_function(1)

    c_open = elem_counter(self,problem_path,'{',"no")
    c_close = elem_counter(self,problem_path,'}',"no")
    if((c_open == c_close) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Number of { , } is " + str(c_open) )
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-18] Number of \n { = " + str(c_open) +  "\n } = " + str(c_close) )
        self.error_function(1)


    check_word_presence(self,"(define",problem_path,"no")
    check_word_presence(self,"(:objects",problem_path,"no")
    check_word_presence(self,"(:init",problem_path,"no")
    check_word_presence(self,"(:domain",problem_path,"no")
    check_word_presence(self,"(problem",problem_path,"no")
    if (self.print_checker == 0):
        self.textBrowser.append("\nCOMPONENTS CHECKS \n")

    if(list_to_string(self,search_keyword(self,"problem",problem_path)).replace("(","").replace(")","").replace(" ","")  == ""):
        if (self.print_checker == 0):
            self.textBrowser.append("[ \u2718 ][ERROR-19] Please specify the problem name")
            self.error_function(1)







    if(elem_counter(self,problem_path,"(:init)","no") > 0):
        init_list = []
    else:
        init_list =    search_keyword(self,"init",problem_path)




    domain_list =  search_keyword(self,"domain",problem_path)
    objects_list = search_keyword(self,"objects",problem_path)
    goal_list =    search_keyword(self,"goal",problem_path)    
    problem_list = search_keyword(self,"problem",problem_path)


    if (not(domain_list == []) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Domain found")
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-20] Domain not found")
        self.error_function(1)
    if (not(objects_list == []) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Objects found")
    elif (self.print_checker == 0):
        self.textBrowser.append("[WARNING-2] Objects not found")
    if (not(init_list == []) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Init found")
    if (not(goal_list == []) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Goal found")
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-22] Goal not found")
        self.error_function(1)

    check_strange_words_problem(self,problem_path,domain_list,problem_list,init_list,goal_list,objects_list)
    if (self.print_checker == 0):
        self.textBrowser.append("\nOBJECTS CHECKS\n")

    objects_to_check = list_to_string(self,objects_list).replace( ")","").replace(":objects","").replace( "(","").replace(" and ","").replace("and","").replace(" not ","").replace("not","").replace(" or ","").strip().split()
    init_objects_to_check = set(list_to_string(self,init_list).replace( ")","").replace(":init","").replace( "(","").replace(" and ","").replace("and","").replace(" not ","").replace("not","").replace(" or ","").strip().split())
    goal_objects_to_check = set(list_to_string(self,goal_list).replace( ")"," ").replace(":goal","").replace( "("," ").replace(" and ","").replace("and","").replace(" not ","").replace("not","").replace(" or ","").strip().split())


    for element in init_objects_to_check:
        if(not(element in objects_to_check)):
            if(not(element in predicate_list)):
                if (self.print_checker == 0):
                    self.textBrowser.append("[ \u2718 ][ERROR-23] Object in (:init) '"+ str(element) + "' isn't present in (:objects) try to add it into (:objects)")
                self.error_function(1)

    if (self.print_checker == 0):
        self.textBrowser.append("[ \u2713 ] Check INIT -> OBJECTS all objects in INIT are present in OBJECTS")
    for element in goal_objects_to_check:
        if(not(element in objects_to_check)):
            if(not(element in predicate_list) and (self.print_checker == 0)):
                self.textBrowser.append("[ \u2718 ][ERROR-24] Object in (:goal) '"+ str(element) + "' isn't present in (:objects) try to add it into (:objects)")
                self.error_function(1)
    if (self.print_checker == 0):
        self.textBrowser.append("[ \u2713 ] Check GOAL -> OBJECTS all objects in GOAL are present in OBJECTS")
     
    
    for element in rest_to_check:
        if(not(element in objects_to_check) and (self.print_checker == 0)):
            self.textBrowser.append("[ \u2718 ][ERROR-25] Object '"+ str(element) + "' isn't present in (:objects) try to add it into (:objects)")
            self.error_function(1)

    check_useless_parenthesis(self,problem_path)

    predicate_form_checker(self,"init",predicate_list,"file",predicates_dict,problem_path)
    predicate_form_checker(self,"goal",predicate_list,"file",predicates_dict,problem_path)

    if (self.print_checker == 0):
        self.textBrowser.append("\n\n")

    if (self.print_checker == 0):
        self.print_checker = 1

    return [list_to_string(self, predicate_list_complete),
            list_actions_Santilli,
            list_to_string(self, init_list),
            list_to_string(self, goal_list),
            list_to_string(self, objects_list)]