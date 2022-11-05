(define
	(domain break)

	(:predicates 
		(broken ?x)
	)

	(:action hammer
		:parameters (?x)
		:precondition ()
		:effect (broken ?x)
	)
)


