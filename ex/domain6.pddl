(define
	(domain move)

	(:requirements :strips)

	(:types object position)

	(:predicates
		(isin ?x - object ?y - position)
		(next ?x ?y - position)
	)

	(:action move
		:parameters (?x - object ?y ?z - position)
		:precondition 
			(and
				(isin ?x ?y)
				(or
					(next ?y ?z)
					(next ?z ?y)
				)
			)
		:effect
			(and
				(not (isin ?x ?y))
				(isin ?x ?z)
			)
	)
)

