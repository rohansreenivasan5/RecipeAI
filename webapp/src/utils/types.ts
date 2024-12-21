interface RecipeBase {
	id: number
	title: string
}

interface Recipe extends RecipeBase {
	directions: string
	url: string
}

interface UserProfile {
	id: number
	name: string
	likes: RecipeBase[]
	dislikes: RecipeBase[]
}