#include "parse.h"

static void parseEnvironment(xmlDocPtr doc, xmlNode *cur_node) {
  char *element;
  char *must = NULL;
  if (env_count >= parameter_array_size) { exit(1); }
  while (cur_node != NULL) {
    if (environment[env_count].count >= variable_array_size) { exit(1); }

    if ((!xmlStrcmp(cur_node->name, (const xmlChar *)"MUST"))) {
      must = ((char *)(xmlNodeListGetString(doc, cur_node->xmlChildrenNode, 1)));
      if (strcmp("true", must) == 0) {
        environment[env_count].must = 1;
      } else if (strcmp("false", must) == 0) {
        environment[env_count].must = 0;
      }
    } else if ((!xmlStrcmp(cur_node->name, (const xmlChar *)"ELEMENT"))) {
        element = ((char *)(xmlNodeListGetString(doc, cur_node->xmlChildrenNode, 1)));

        if (strlen(element) < parameter_strings_long) {
            int p = environment[env_count].count;
            strncpy(environment[env_count].environment[p], element,
                    strlen(element));
        } else {
            exit(1);
        }
        environment[env_count].count++;

    } else if ((!xmlStrcmp(cur_node->name, (const xmlChar *)"NAME"))) {
        element = ((char *)(xmlNodeListGetString(doc, cur_node->xmlChildrenNode, 1)));

        if (strlen(element) < parameter_strings_long) {
            strncpy(environment[env_count].name, element,
                    strlen(element));
        } else {
            exit(1);
        }
    }
    cur_node = cur_node->next;
  }
  env_count++;
}

static void parseArgument(xmlDocPtr doc, xmlNode *cur_node) {
  char *element;
  char *must = NULL;
  if (argv_count >= parameter_array_size) { exit(1); }
  while (cur_node != NULL) {
    if (argument[argv_count].count >= variable_array_size) { exit(1); }

    if ((!xmlStrcmp(cur_node->name, (const xmlChar *)"MUST"))) {
      must = ((char *)(xmlNodeListGetString(doc, cur_node->xmlChildrenNode, 1)));
      if (strcmp("true", must) == 0) {
        argument[argv_count].must = 1;
      } else if (strcmp("false", must) == 0) {
        argument[argv_count].must = 0;
      }
    } else if ((!xmlStrcmp(cur_node->name, (const xmlChar *)"ELEMENT"))) {
      element = ((char *)(xmlNodeListGetString(doc, cur_node->xmlChildrenNode, 1)));

      if (strlen(element) < parameter_strings_long) {
        int p = argument[argv_count].count;
        strncpy(argument[argv_count].argument[p], element,
                strlen(element));
      } else {
        exit(1);
      }

      argument[argv_count].count++;
    }
    // else if ((!xmlStrcmp(cur_node->name, (const xmlChar *)"text"))) {
    // }
    cur_node = cur_node->next;
  }
  argv_count++;
}

static void parseRoot(xmlDocPtr doc, xmlNode *a_node) {
    a_node = a_node->children;
    xmlNode *cur_node = NULL;

    for (cur_node = a_node; cur_node; cur_node = cur_node->next) {
        if (!(xmlStrcmp(cur_node->name, (const xmlChar *)"ENVIRONMENT"))) {
            parseEnvironment(doc, cur_node->xmlChildrenNode);
        }
        else if (!(xmlStrcmp(cur_node->name, (const xmlChar *)"ARGUMENT"))) {
            parseArgument(doc, cur_node->xmlChildrenNode);
        }
    }
    return;
}

void print_parse_result() {
    int i, j;
    for (i = 0; i < env_count; i++) {
        printf("[ENVIRONMENT %d]\n",i+1);
        printf("[NAME]: %s\n",environment[i].name);
        printf("[ELEMENT COUNT]: %d\n", environment[i].count);
        for (j = 0; j < environment[i].count; j++) {
            printf("%s\n", environment[i].environment[j]);
        }
    }
    printf("[ENVIRONMENT COUNT]: %d\n\n", env_count);

    for (i = 0; i < argv_count; i++) {
        printf("[ARGUMENT %d]\n",i+1);
        printf("[MUST]: %d\n", argument[i].must);
        printf("[ELEMENT COUNT]: %d\n", argument[i].count);
        for (j = 0; j < argument[i].count; j++) {
            printf("%s\n", argument[i].argument[j]);
        }
    }
    printf("[ARGUMENT COUNT]: %d\n", argv_count);
}

void parse_xml(char *xml_posion){
    xmlDoc * doc = NULL;
    xmlNode *root_element = NULL;

    LIBXML_TEST_VERSION
    /*parse the file and get the DOM */
    doc = xmlReadFile(xml_posion, NULL, 0);
    if (doc == NULL) { printf("Error: could not parse file %s\n", xml_posion); }
    /*Get the root element node */
    root_element = xmlDocGetRootElement(doc);

    parseRoot(doc, root_element);

    xmlFreeDoc(doc);
    xmlCleanupParser();
    print_parse_result();
}