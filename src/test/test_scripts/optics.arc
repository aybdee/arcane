Define convex_lens as lens with focal length -1 and thickness 1 at (-1,0) 
Define concave_lens as lens with focal length 1 and thickness 1 right of convex_lens
Define second_convex as lens with focal length -1 and thickness 1 right of concave_lens

Define incoming_rays as rays from (-4, -0.2) to (-4, 0.2) with direction RIGHT and count 4
@propagate incoming_rays through convex_lens then concave_lens
@transform convex_lens to lens with focal length -5 and thickness 1 at (-1,0) 

# @write "rays diverge" below convex_lens with size 20
# @write "rays converge" above concave_lens with size 20
# @write "rays diverge again" below second_convex  with size 20
