(define(domain robot-cup-domain)
(:requirements :strips)
(:predicates (at ?what ?to )
             (pos ?x)
             (cup ?x)
             (empty ?x)
)
(:action move
:parameters (?what ?from ?to)
:precondition (and
              (cup ?what)
              (empty ?to)
              (pos ?from)
              (pos ?to)
              (at ?what ?from)
              )
:effect ()

)


)
