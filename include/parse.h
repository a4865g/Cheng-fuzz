#include <stdio.h>
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <stdlib.h>
#include <string.h>

#define parameter_array_size 300
#define parameter_strings_long 700
#define variable_array_size 30

struct environment_list {
    _Bool must;
    int count;
    char name[parameter_strings_long];   
    char environment[variable_array_size][parameter_strings_long];
};

struct argument_list {
    _Bool must;
    int count;
    char argument[variable_array_size][parameter_strings_long];
};

struct environment_list environment[parameter_array_size];
int                   env_count;

struct argument_list argument[parameter_array_size];
int                   argv_count;

void parse_xml(char *xml_posion);