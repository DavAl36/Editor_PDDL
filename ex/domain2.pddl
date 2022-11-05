(define
	(domain envelope)

	(:predicates
		(letter_in_envelope)
		(envelope_sealed)
	)

	; can put the gift in the box only if not already and the box is not
	; yet sealed
	(:action put_in
		:precondition
			(and (not (letter_in_envelope)) (not (envelope_sealed)))
		:effect (letter_in_envelope)
	)

	; can seal the envelope again, so no preconditions 
	(:action seal
		:precondition ()
		:effect (envelope_sealed)
	)
)


