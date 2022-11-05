(define 
	(domain  hospital)

	(:types
		person
		doctor - person
		surgeon - doctor
		allergist - doctor
	)

	(:predicates 
		(breath ?person)
		(hearth ?person)
	)

	(:action cpr
		:parameters  (?x - doctor ?y - person)
		:precondition  (not (breath ?y))
		:effect  (breath ?y)
	)

	(:action surgery
		:parameters  (?x - surgeon ?y - person)
		:precondition 
			(and
				(breath ?y)
				(not (hearth ?y))
			)
		:effect  (hearth ?y)
	)
)
