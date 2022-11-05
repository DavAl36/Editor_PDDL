import sys
from file_checker import *
import re
import svgwrite


def list_duplicates_of(self,seq,item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item,start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs



def parenthesis_index(self,path,what_check,open_par,close_par):#(problem,'(')
    '''
    Fa il conteggio delle parentesi aperte e chiuse

    parenthesis_index(problem_path,"OPENED","(",")")) restituisce dove hai aperto una tonda per sbaglio

    parenthesis_index(problem_path,"CLOSED","(",")")) restituisce dove hai chiuso una tonda per sbaglio

    '''
    c_open = 0
    c_close = 0
    index = 0
    
    reverse_file = []
    maximum_length = 0
    
    if(what_check == "OPENED"):
        file = open(path,"r")
        for line in file:
            reverse_file.insert(0,line)
            maximum_length = maximum_length + 1
        #self.textBrowser.append(reverse_file)
        file.close()
        file = open(path,"r")
        for line in reverse_file:
            for element in line:
                if(open_par in element):
                    c_open = c_open + 1
                if(close_par in element):
                    c_close = c_close + 1
                #self.textBrowser.append("DIFF = " + str(c_open-c_close))
                if(c_open-c_close == 0):
                    return maximum_length-index
            index = index + 1
        file.close()
        return maximum_length-index
    if(what_check == "CLOSED"):

        file = open(path,"r")
        for line in file:
            for element in line:
                if(open_par in element):
                    c_open = c_open + 1
                if(close_par in element):
                    c_close = c_close + 1
                #self.textBrowser.append("DIFF = " + str(c_open-c_close))
                if(c_open-c_close == 0):
                    return index
            index = index + 1
        file.close()
        return index

def elem_counter(self,path,what,show_print):#(problem,'(')
    counter = 0
    flag = 0
    
    file = open(path,"r")

    if(len(what) == 1):#se what è un carattere
        if((show_print == "yes") and (self.print_checker == 0)):
            self.textBrowser.append("[ELEM_COUNTER] ---> what è una parola '" + str(what) + "' di lunghezza  " + str(len(what)) )
        for line in file:
            for element in line:
                if(what == element):
                    if((show_print == "yes") and (self.print_checker == 0)):
                        self.textBrowser.append("[ELEM_COUNTER] ---> In line -> " + str(line) + "  found -> " + str(what) )
                    counter = counter+1    
    else:#what è una parola
        if((show_print == "yes") and (self.print_checker == 0)):
            self.textBrowser.append("[ELEM_COUNTER] ---> what è una parola '" + str(what) + "' di lunghezza  " + str(len(what)) )
        for line in file:
            for element in line.strip().split():
                if(what == element):
                    
                    if((show_print == "yes") and (self.print_checker == 0)):
                        self.textBrowser.append("[ELEM_COUNTER] ---> In line -> " + str(line) + "  found -> " + str(what) )
                    #if(len(what) == len(element) ): 
                        # questo controllo risolve il seguente problema
                        # se ho controllo problem in problema deve ritornarmi false
                        # perchè non è la stessa parola
                    counter = counter+1

    file.close()

    return counter


def check_word_presence(self,word,problem_path,show_print):
    '''
    usata per controllo di chiave 
    il numero di volte che la parola chiave viene ripetuta deve sempre essere 1 !!!
    '''
    c_word = elem_counter(self,problem_path,word,show_print)

    if((c_word == 0) and (self.print_checker == 0)):
        self.textBrowser.append("[WARNING-1] Element '"+ str(word) +"' NOT present in the file")
        #sys.exit("")
    if((c_word == 1) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] Element '" + str(word) + "' present in the file")
    if((c_word > 1) and (self.print_checker == 0)):
        self.textBrowser.append("[ERROR-1] Element '"+ str(word) +"'  present "+str(c_word)+  " many times")
        self.error_function(1)
        #sys.exit("")


def list_to_string(self,lista):
    '''
    convert list to string
    '''
    out = ""
    for digit in lista:
        out += str(digit)
    return out


def search_keyword(self,word_to_check,problem_path):
    '''
    restituisce tutto il blocco della word_to_check di un file
    '''
    c_open = 1
    c_close = 0
    diff_c = 0
    status = "" 
    char_list = []
    output_list = []
    start_copy = 0
    keyword = ""
    char_start = ""
    limit_diff = 0
    '''
    se word_to_check è un azione
        estrapolo in il nome dell'azione e lo salvo in action_name

    scorro tutte le linee del file
        se c'è la parola action e la parola action_name
        scorro tutti gli elementi della linea e gli aggiugo a char_list
            se un elemento è ' ' o '\n' o '\t' 
                decido i limiti per le varie keyword
                salvo in keyword la parola
                    se wordcheck è in keyword
                        aggiorno stato
                        il contatore delle ( parte da +1
                            aggiungo la keyword alla lista output
                        svuoto char_list
                    se l'elemento è ( e status è keyword
                        contatore ( +1
                    se l'elemento è ) e status è keyword
                        contatore ) +1
                    faccio la differenza di questi contatori in  diff_c
                    se status == word_to_check
                        aggiungo ultimo elemento ad output_list
                        se la diff_c == 0
                            Vuol dire che va chiusa la parentesi
    '''
    action_name = "granturchese1900"

    if("action" in word_to_check):
        action_name = word_to_check.replace("action", '' )
        #self.textBrowser.append("TROVATA ACTION: " + str(action_name))
        word_to_check= "granturchese1900"

    
    file = open(problem_path,"r")
    for line in file:
        for element in line:
            if("(:action" in line):
                if(action_name in line):
                    #self.textBrowser.append("GUGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                    word_to_check = "action"
            char_list.append(element)#add char to list
            if( (element == ' ') or(element == '\n') or (element == '\t') ):
                keyword = list_to_string(self,char_list)
                #self.textBrowser.append(keyword)
                if(word_to_check == "problem" or word_to_check == "define"):
                    char_start = "("
                else:
                    char_start = "(:"
                if(word_to_check == "(domain" ):
                    char_start = ""
                #self.textBrowser.append((char_start+str(word_to_check)))
                if((char_start+str(word_to_check))in keyword):
                    status = word_to_check
                    output_list.append("(")
                    for agg in keyword: #add keyword to the output list
                        if(agg == ":" ):
                            start_copy = 1
                        if(start_copy == 1):
                            output_list.append(agg)
                    start_copy = 0
                del char_list[:]
            if( ("(" in element)and(status == word_to_check) ):
                c_open = c_open + 1
            if( (")" in element)and(status == word_to_check) ):
                c_close = c_close + 1
            diff_c = c_open-c_close
            if(status == word_to_check):
                output_list.append(element)
                if(diff_c == limit_diff):
                    status = ""
                    return output_list
    file.close()
    return []



def search_keyword_string(self,word_to_check,file):
    '''
    restituisce tutto il blocco della word_to_check di una stringa
    differenze in:

                if(word_to_check == "precondition" or word_to_check == "effect"):
                    char_start = ":"
                if(word_to_check == "parameters"):
                    char_start = ":"
                    c_open = 0
                    limit_diff = -1

                if(diff_c == limit_diff or element == ":"):
 
    '''
    c_open = 1
    c_close = 0
    diff_c = 0
    status = "" 
    char_list = []
    output_list = []
    start_copy = 0
    keyword = ""
    char_start = ""
    limit_diff = 0
    '''

    '''
    action_name = "granturchese1900"

    if("action" in word_to_check):
        action_name = word_to_check.replace("action", '' )
        #self.textBrowser.append("TROVATA ACTION: " + str(action_name))
        word_to_check= "granturchese1900"

    for line in file:
        for element in line:
            if("(:action" in line):
                if(action_name in line):
                    #self.textBrowser.append("GUGGGGGGGGGGGGGGGGGGGGGGGGGGG")
                    word_to_check = "action"
            char_list.append(element)#add char to list
            if( (element == ' ') or(element == '\n') or (element == '\t') ):
                keyword = list_to_string(self,char_list)
                #self.textBrowser.append(keyword)
                if(word_to_check == "problem" or word_to_check == "define"):
                    char_start = "("
                else:
                    char_start = "(:"
                if(word_to_check == "precondition" or word_to_check == "effect"):
                    char_start = ":"
                if(word_to_check == "parameters"):
                    char_start = ":"
                    c_open = 0
                    limit_diff = -1


                #self.textBrowser.append((char_start+str(word_to_check)))
                if((char_start+str(word_to_check))in keyword):
                    status = word_to_check
                    output_list.append("(")
                    for agg in keyword: #add keyword to the output list
                        if(agg == ":" ):
                            start_copy = 1
                        if(start_copy == 1):
                            output_list.append(agg)
                    start_copy = 0
                del char_list[:]
            if( ("(" in element)and(status == word_to_check) ):
                c_open = c_open + 1
            if( (")" in element)and(status == word_to_check) ):
                c_close = c_close + 1
            diff_c = c_open-c_close
            #if(status == "precondition"):
            #    self.textBrowser.append(str(element) + "   c_open: " + str(c_open) + "   c_close: " + str(c_close) + "   diff_c: " + str(diff_c))
            if(status == word_to_check):
                if(not(element == ":")):
                    output_list.append(element)
                if(diff_c == limit_diff or element == ":"):
                    status = ""
                    return output_list
    file.close()
    return []

    delete_comments(self,source_path,problem_path)

def file_replace_word(self,file_with_word,file_without_word ,word_to_find,word_to_preplace ):

    '''
    sostituisce una parola o più parole all'interno di un file
    '''
    f = open(file_with_word,'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace(word_to_find,word_to_preplace)

    f = open(file_without_word,'w')
    f.write(newdata)
    f.close()


def delete_comments(self,file_with_comments,file_to_save_result):

    '''
    Prende un file con i commenti e li scommenta

    '''
    file = open(file_with_comments,"r")
    file_without_comment = open(file_to_save_result,"w")
    flag_comment = 0
    counter = 0
    for line in file:
        for element in line:
            #self.textBrowser.append(element)
            if(element == ";"):
                #self.textBrowser.append("Start COMMENT")
                flag_comment = 1

            if( (flag_comment == 1)and(element == "\n") ):
                flag_comment = 0
                counter = counter+1
                #self.textBrowser.append("Fine linea")

            if(flag_comment == 0):
                file_without_comment.write(element)
                #self.textBrowser.append("SCRIVO SU FILE")
    if (self.print_checker == 0):
        self.textBrowser.append("\nFound " + str(counter) + " comments in " + file_with_comments)
    file.close()
    file_without_comment.close()



def check_strange_words_problem(self,problem_path,domain_list,problem_list,init_list,goal_list,objects_list):
    '''                         
    Controlla se ci sono parole fuori dalle tonde che devono essere eliminate
    '''
    file = open(problem_path,"r")
    output = []
    for line in file:
        for element in line:
            output.append(element)
    file.close()



    s1 = list_to_string(self,output).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s2 = list_to_string(self,domain_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s3 = list_to_string(self,problem_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s4 = list_to_string(self,init_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s5 = list_to_string(self,goal_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s6 = list_to_string(self,objects_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')

    s1 = set(s1.strip().split(' '))
    s2 = set(s2.strip().split(' '))
    s3 = set(s3.strip().split(' '))
    s4 = set(s4.strip().split(' '))
    s5 = set(s5.strip().split(' '))
    s6 = set(s6.strip().split(' '))
    
    check_other_words = s1.difference(s2).difference(s3).difference(s4).difference(s5).difference(s6)
    check_other_words -= {'problem','define'}
    file = open(problem_path,"r")
    output = []
    counter = 1
    if((len(check_other_words) == 0) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] There aren't strange words")
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-2] There are strange words")
        self.error_function(1)
        self.textBrowser.append(str(check_other_words))
        for word in check_other_words:
            for line in file:
                if((word in line) and (self.print_checker == 0)):
                    self.textBrowser.append("[ERROR-3] strange word '" + str(word) + "' in line " +str(counter))
                    self.error_function(1)
                counter = counter+1
    file.close()



def check_strange_words_domain(self,problem_path,domain_list,requirements_list,list_actions_Santilli,predicate_list_complete,types_list):
    '''
    Controlla se ci sono parole fuori dalle tonde che devono essere eliminate
    '''
    file = open(problem_path,"r")
    output = []
    for line in file:
        for element in line:
            output.append(element)
    file.close()


    s1 = list_to_string(self,output).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s2 = list_to_string(self,domain_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s3 = list_to_string(self,requirements_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s4 = list_to_string(self,list_actions_Santilli).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s5 = list_to_string(self,predicate_list_complete).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')
    s6 = list_to_string(self,types_list).replace('\n', ' ').replace('\t', ' ').replace('(', ' ').replace(')', ' ')

    s1 = set(s1.strip().split(' '))
    s2 = set(s2.strip().split(' '))
    s3 = set(s3.strip().split(' '))
    s4 = set(s4.strip().split(' '))
    s5 = set(s5.strip().split(' '))
    s6 = set(s6.strip().split(' '))

    check_other_words = s1.difference(s2).difference(s3).difference(s4).difference(s5).difference(s6)
    '''
    self.textBrowser.append("..................................................")
    self.textBrowser.append(s1)
    self.textBrowser.append("..................................................")
    self.textBrowser.append(s2)
    self.textBrowser.append("..................................................")
    self.textBrowser.append(s3)
    self.textBrowser.append("..................................................")
    self.textBrowser.append(s4)
    self.textBrowser.append("..................................................")
    self.textBrowser.append(s5)
    self.textBrowser.append("..................................................")
    '''
    check_other_words -= {'problem','define',':predicates','domain',":types"}

    #self.textBrowser.append(check_other_words)
    #self.textBrowser.append("..................................................")
    file = open(problem_path,"r")
    output = []
    counter = 1
    if((len(check_other_words) == 0) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] There aren't strange words")
    elif (self.print_checker == 0):
        self.textBrowser.append("[ \u2718 ][ERROR-4] There are strange words")
        self.error_function(1)
        self.textBrowser.append(check_other_words)
        for word in check_other_words:
            for line in file:
                if((word in line) and (self.print_checker == 0)):
                    self.textBrowser.append("[ \u2718 ][ERROR-5] strange word '" + str(word) + "' in line " +str(counter))
                    self.error_function(1)
                counter = counter+1
    file.close()

def check_useless_parenthesis(self,path):
    '''
    Controlla che non ci sono coppie di parentesi aperte inutilmente
    '''
    counter = 0
    flag = 0
    file = open(path,"r")
    for line in file:
        for element in line:
            if(flag == 1):
                if(element == ' '):
                    continue
                if( (element == '(') or (element == ')') and (self.print_checker == 0)):
                    #self.textBrowser.append("[ERROR-6] In line " +str(counter)+ " there is a useless parenthesis")
                    #sys.exit("")
                    self.textBrowser.append("[WARNING-6] In line " +str(counter)+ " there is a useless parenthesis")
                    flag= 0
            if(element == '('):
                flag = 1
            else:
                flag = 0
        counter = counter+1
    file.close()
    if (self.print_checker == 0):
        self.textBrowser.append("[ \u2713 ] There aren't useless parenthesis")


def predicates_extracter(self,list_to_check):
    '''
    prende il file domain
    estrae la parte di predicates
    la pulisce
    e crea un dizionario con (nome predicato, elementi del predicato)
    '''
    predicates_dict = {}
    counter = 0
    old_element = ""
    predicate_l = list_to_string(self,list_to_check).replace(':predicates',' ').replace('(',' ').replace(')',' ').strip().split()
    #self.textBrowser.append(predicate_l)
    new_predicate_l = predicate_l
    index_to_remove = []
    #--------delete types from predicate
    for element in predicate_l:
        if(element == '-'):
            index_to_remove.append(counter)
            index_to_remove.append(counter+1)
        counter = counter + 1 
    counter = 0
    for idx in index_to_remove:
        del new_predicate_l[idx-counter]
        counter = counter+1
    counter = 0
    if (self.print_checker == 0):
        self.textBrowser.append(str(new_predicate_l))
    #---------------------------------------------
    for element in new_predicate_l:
        if (not('?' in element)):
            #self.textBrowser.append("OK")
            predicates_dict.update({element: counter})
            old_element = element
            counter = 0
        else:
            counter = counter +1
            predicates_dict.update({old_element: counter})
    return predicates_dict


def predicate_form_checker(self,what,pre_list,typeF,predicates_dict,problem_path):
    lista = ""

    where_name=""
    element = ""
    if(typeF == "file"):
        where_name = what
        lista = list_to_string(self,search_keyword(self,what,problem_path)).replace(what,' ').replace(':',' ').replace('(',' ').replace(')',' ').strip().split() 
    if(typeF == "string"):
        if("precondition" in list_to_string(self,what)):
            lista = list_to_string(self,what).replace("precondition",' ').replace(':',' ').replace('(',' ').replace(')',' ').strip().split() 
            where_name = "precondition"
        if("effect" in list_to_string(self,what)):
            lista = list_to_string(self,what).replace("effect",' ').replace(':',' ').replace('(',' ').replace(')',' ').strip().split() 
            where_name = "effect"
    #self.textBrowser.append(lista)

    '''
    decido che cosa analizzare 
    se un file 
    o una stringa

    scorro elementi
        se element è diverso da and,or,not,when
            se element è un predicato
                vedo quanti elementi ha quel predicato
                se counter+ numero di elementi del predicato non superano il numero di elementi della lista
                    conto da 0  a n_el
                        se l'elemento della lista a counter+c è un predicato o è and,or,not,when
                            allora è un errore
            altirmenti
                aggiorno contatore errore
                se il contatore è maggiore degli elementi dell'ultimo predicato
                    allora ho più elementi in quel predicato e quindi ho errore.               
    '''
    #self.textBrowser.append(lista)
    counter = 0
    counter_error = 0
    n_el = 0
    list_length = len(lista)
    predicate = ""

    for element in lista:
        #if(where_name == "effect"):
        #    self.textBrowser.append(element)
        if((element != 'and')and(element != 'or')and(element != 'not')and(element != 'when')):
            #self.textBrowser.append("ELEMENT:" +str(element))
            if(element in pre_list):
                counter_error=0
                predicate = element
                n_el = predicates_dict[element] +1
                #self.textBrowser.append(predicates_dict[element])
                #self.textBrowser.append("elemento "+str(element)+ " nella lista dei predicati n_el: "+str(n_el-1))
                if( (counter+n_el) <= list_length):#evita di uscire dall array
                    for c in range(1,n_el):
                        #self.textBrowser.append("    @@@@@@@@@"+ str(lista[counter+c]) )
                        l = lista[counter+c]
                        if(l in pre_list)or(l == 'and')or(l == 'not')or(l == 'or')or(l == 'when'):
                            if (self.print_checker == 0):
                                self.textBrowser.append("[ \u2718 ][ERROR-7] Predicate '"+str(element)+ "' in "+str(where_name) + " needs to have '"+str(n_el-1)+"' elements " )
                                self.error_function(1)
                                #sys.exit("")

            else:
                #self.textBrowser.append("Conteggio " + str(n_el-1))
                #self.textBrowser.append("ELEMENT:" +str(element))
                counter_error=counter_error+1
                if((counter_error > n_el-1) and (self.print_checker == 0)):
                    self.textBrowser.append("[ \u2718 ][ERROR-8] Word '"+str(element)+"' cannot stay inside the predicate '"+str(predicate)+"' in function: "+str(where_name))
                    self.error_function(1)
                    #sys.exit("")
                #self.textBrowser.append(counter_error)
        counter = counter+1
    # check for the last word, if contains 0 elements there is an erro

    if( (not(element == '')) and (counter_error == 0) and  (not(predicates_dict[element] == 0)) ):
        if (self.print_checker == 0):
            self.textBrowser.append("[ \u2718 ][ERROR-9] Word '"+str(element)+"' in function: "+ str(where_name) + " needs an element")
            self.error_function(1)
        #sys.exit("")
    #self.textBrowser.append(counter_error)
def get_action_names(self,path,n):
    #Restituisce una lista col nome di tutte le azioni
    counter = 0
    ind = 0
    flag_name = 0
    name_list = []
    file = open(path,"r")
    for line in file:
        LINE = line.strip().split()
        for element in LINE:
            if(element == "(:action"):
                counter = counter+1
                ind = LINE.index(element)
                name_list.append(LINE[ind+1])
    file.close()
    if(n == counter):
        # controllo se ci sono doppi nomi
        duplicates_name_list = []
        for int_name in name_list:  
            duplicates_name_list.append(list_duplicates_of(self,name_list, int_name))
        for el in duplicates_name_list:
            #self.textBrowser.append(len(el))
            if((len(el) > 1) and (self.print_checker == 0)):
                 self.textBrowser.append("[ \u2718 ][ERROR-27] There "+str(len(duplicates_name_list)) + " actions with the same name")
                 self.error_function(1)
                 flag_name = 1 
                 #sys.exit("")
            elif (self.print_checker == 0):
                flag_name = 0
    if((flag_name == 0) and (self.print_checker == 0)):
        self.textBrowser.append("[ \u2713 ] There are "+str(counter) + " actions: " +str(name_list) )

    elif (self.print_checker == 0):
        self.textBrowser.append(counter)
        self.textBrowser.append(n)
        self.textBrowser.append("[ \u2718 ][ERROR-10] There are not the right number of actions")
        self.error_function(1)
    return name_list

'''
def get_action_names(path,n):
    #Restituisce una lista col nome di tutte le azioni
    counter = 0
    ind = 0
    name_list = []
    file = open(path,"r")
    for line in file:
        LINE = line.strip().split()
        for element in LINE:
            if(element == "(:action"):
                counter = counter+1
                ind = LINE.index(element)
                name_list.append(LINE[ind+1])
    file.close()
    if(n == counter):
        self.textBrowser.append("[ \u2713 ] There are "+str(counter) + " actions: " +str(name_list) )


    else:
        self.textBrowser.append(counter)
        self.textBrowser.append(n)
        self.textBrowser.append("[ \u2718 ][ERROR-10] There are not the right number of actions")
    return name_list

'''

# SVG

def bracket_split_in_list(string):
    supportString = string
    resList = []
    while (len(supportString) > 1):
        currentOpenBracket = supportString.find("(")
        currentClosedBracket = supportString.find(")")
        nextOpenBracket = supportString.find("(", (currentOpenBracket + 1))

        while ((nextOpenBracket < currentClosedBracket) and nextOpenBracket != -1):
            currentClosedBracket = supportString.find(")", (currentClosedBracket + 1))
            nextOpenBracket = supportString.find("(", (nextOpenBracket + 1))

        resList.append(supportString[currentOpenBracket:currentClosedBracket + 1])
        supportString = supportString[currentClosedBracket + 1:]

    return resList

def delete_keyword(baseString, deleteString):
    deleteString = deleteString + '[\s(]+'
    baseString = re.sub(deleteString, '', baseString)
    baseString = re.sub('^[\s]*', '', baseString)
    openBracketAmount = baseString.count("(")
    closedBracketAmount = baseString.count(")")
    if (openBracketAmount > closedBracketAmount):
        baseString = re.sub('^[(]', '', baseString)
    if (closedBracketAmount > openBracketAmount):
        baseString = re.sub('[)]$', '', baseString)
    baseString = re.sub('[\n\s\t]', '', baseString)
    baseString = baseString.replace(')(', ') (')

    return baseString
