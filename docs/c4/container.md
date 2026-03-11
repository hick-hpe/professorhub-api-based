# Containers

> Detalha o que compõe o sistema, como aplicações web, bancos de dados, microsserviços ou sistemas de mensageria.

## Script PlantUML

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(docente, "Docente")

System_Boundary(professorhub, "ProfessorHub") {

    Container(webapp, "Aplicação Django", "Python/Django", "Sistema principal")

    Container(db, "Banco de Dados", "PostgreSQL", "Armazena dados")
}


Rel(docente, webapp, "Acessa pelo navegador")
Rel(webapp, db, "Lê e grava dados")

@enduml
```
