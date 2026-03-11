# Contexto

Mostra o sistema principal e como ele interage com usuários e sistemas externos.

## Script PlantUML

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(docente, "Docente", "Planeja aulas")

System(professorhub, "ProfessorHub", "Sistema de planejamento de aulas")

System_Ext(classroom, "Google Classroom", "Sistema externo")
System_Ext(gmail, "Gmail", "Serviço de email")

Rel(docente, professorhub, "Utiliza o sistema")
Rel(professorhub, gmail, "Envia emails")
Rel(professorhub, classroom, "Integra atividades")

@enduml
```
