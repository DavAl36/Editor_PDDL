(define (problem MonkeyBananaProblemProblem)
			(:domain MonkeyBananaProblemDomain)
			
			(:objects 	Monkey Banana Box
						p0 p1 p2
			)
			
			(:init		(monkey Monkey)
						(banana Banana)							
						(box Box)
						(position p0) (position p1) (position p2)
						(at Monkey p0) (at box p2)
						(adj p0 p1) (adj p1 p0)
						(adj p1 p2) (adj p2 p1)
						(bananaPosition p1)
						(isBananaGrabbed Banana)

			)
			
			(:goal	    (and(not(isBananaGrabbed Banana)))
			)
)
