pykachu
=======

Monitoramento de tarefas em background usando redis como backend


Configuração
============

Para usar a classe JobServer é preciso ter uma variavel de ambiente com o nome PYKACHU_REDIS_SERVER contendo
o IP do servidor Redis que será usado.

Alternativamente pode-se sobrescrever a propriedade REDIS_HOST do módulo pykachu