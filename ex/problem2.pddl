; a STRIPS-like planning problem

(define
	; the name of this specific problem
	(problem doall)

	; the domain, defined in another file
	(:domain envelope)

	; initial state
	(:init)

	; the goal
	(:goal
		(and (letter_in_envelope) (envelope_sealed))
	)
)


