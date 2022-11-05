(define
	(domain over)

	(:requirements :strips :conditional-effects)

	(:predicates
		(box_closed)
		(item_in)
		(item_over)
	)

	(:action put_on
		:precondition () 
		:effect
			(and 
				(when (box_closed) (item_over))
				(when (not (box_closed)) (item_in))
			)
	)

	(:action open
		:precondition
			(and 
				(box_closed)
				(not (item_over))
			)
		:effect
			(and
				(not (item_over))
				(not (box_closed))
			)
	)
)


