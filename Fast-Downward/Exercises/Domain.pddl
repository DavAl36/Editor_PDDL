(define
	(domain simple)

	(:requirements :strips)

	; boolean variables x and y
	(:predicates
		(x)
		(y)
	)

	; if x is true, this action makes both x and y false
	(:action a
		:precondition (x)
		:effect (and (not (x)) (not (y)))
	)

	; if x is false, this action makes y true
	(:action b
		:precondition (not (x))
		:effect (y)
	)
)
