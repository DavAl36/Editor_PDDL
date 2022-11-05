(define (domain domino-MARRtino)
(:requirements :strips)
(:predicates (at ?from ?to)
             (adj ?sq1 ?sq2)
             (rob ?x)
             (wet ?room)
             (visitor ?x)
             (light ?x)
             (explained ?x)
)

(:action move
    :parameters (?who ?from ?to)
    :precondition(and 
                 (at ?who ?from)
                 (rob ?who)
                 (adj ?from ?to)
                 (not (wet ?to))
                 )
    :effect (and(not(at ?who ?from))(at ?who ?to))
)    
(:action speak
    :parameters (?who ?atwho ?where)
    :precondition (and
                  (rob ?who)
                  (visitor ?atwho)
                  (at ?who ?)
                  (at ?atwho ?where)
                  (light on)
                 ; (not(explained ?where));; aggiunto da me
                  ;; prova ad aggiungere wet
    )
    :effect(explained ?atwho)
)


  (:action turnOn
    :parameters (?a)
    :precondition (and 
           (rob ?a)
           (at ?a sq-1-1)
           (not (light on)))
    :effect  (light on)
    )

    ;(:action turnOn
;    :parameters(?who ?where)
;    :precondition(and
;                 (rob ?who)
;                 (at ?who ?where)
;                 (not(light on))
;    )
;    :effect(light on)
;)
)

