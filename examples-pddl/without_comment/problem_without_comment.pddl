(define 
    (problem  julius)

    (:domain  hospital)

    (:objects 
        julius - person
        frank - allergist
        robert - surgeon
    )

    (:init
        (not (breath julius))
        (not (hearth julius))
    )

    (:goal 
        (and
            (breath julius)
            (hearth julius)
        )
    )
)
