(define
	(domain wash)

	(:requirements :strips)

	(:predicates
		(bucket_filled)
		(car_clean)
	)

	(:action fill
		:precondition (not (bucket_filled))
		:effect (bucket_filled)
	)

	(:action wash
		:precondition (bucket_filled)
		:effect (and (car_clean) (not (bucket_filled)))
	)
)


