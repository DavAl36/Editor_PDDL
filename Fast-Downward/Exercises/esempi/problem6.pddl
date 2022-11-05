(define
	(problem house)

	(:domain move)

	(:objects
		chair table - object
		kitchen corridor bedroom - position
	)

	(:init
		(isin chair kitchen)
		(isin table kitchen)
		(next kitchen corridor)
		(next bedroom corridor)
	)

	(:goal
		(isin chair bedroom)
	)
)

        
