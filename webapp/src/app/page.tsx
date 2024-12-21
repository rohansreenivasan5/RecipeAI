import { cookies } from "next/headers";
import { RegisterButton } from "./_components/RegisterButton";
import { redirect } from "next/navigation";
import {
  getRecipeFeed,
  getUserProfile,
  registerUser,
  updateUserPreference,
} from "@/utils/requests";
import { RecipeCard } from "./_components/RecipeCard";

interface RecipeFeedProps {
  userId: string;
}

const RecipeFeed: React.FC<RecipeFeedProps> = async ({ userId }) => {
  const user = await getUserProfile(userId);
  async function handleLike(recipeId: number, like: 1 | -1) {
    "use server";
    await updateUserPreference(userId, recipeId, like);
  }
  const likedIds = new Set(user.likes.map((recipe) => recipe.id));
  const dislikedIds = new Set(user.dislikes.map((recipe) => recipe.id));
  const recipes = await getRecipeFeed(userId, 24);
  return (
    <div className="flex flex-col items-center">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 p-8 pt-0 pb-20 gap-12 max-w-[1024px] font-[family-name:var(--font-geist-sans)]">
        <div className="col-span-1 md:col-span-2 lg:col-span-3 sticky top-0 p-8 max-md:pb-0 -mx-8 bg-white flex">
          <h1 className="text-lg font-bold">🍳 Recipe Board</h1>
          <div className="flex-grow" />
          <span>Hi, {user.name}!</span>
        </div>
        <div className="col-span-1 md:col-span-2 lg:col-span-3 -mb-4 text-gray-600">
          <span>Recipes that you might like:</span>
        </div>
        {recipes.map((recipe) => (
          <RecipeCard
            recipe={recipe}
            liked={
              likedIds.has(recipe.id) ? 1 : dislikedIds.has(recipe.id) ? -1 : 0
            }
            onLike={handleLike}
          />
        ))}
      </div>
    </div>
  );
};

const USER_ID_COOKIE_KEY = "user_id";

const FOOD_OPTIONS = [
  "Burger",
  "Salad",
  "Pizza",
  "Pasta",
  "Noodle",
  "Rice",
  "Stew",
  "Wrap",
  "Burrito",
  "Sushi",
  "Dumpling",
  "Cake",
  "Cookie",
  "Soup",
  "Barbecue",
];

const RegisterUser = () => {
  async function handleSubmit(formData: FormData) {
    "use server";

    const newUserId = await registerUser(
      formData.get("name") as string,
      formData.get("favorite-food") as string
    );
    const cookieStore = await cookies();
    cookieStore.set(USER_ID_COOKIE_KEY, newUserId);

    redirect("/"); // Reload the page to show the RecipeReed
  }

  return (
    <div className="flex flex-col items-center">
      <form
        action={handleSubmit}
        className="flex flex-col justify-center p-8 pb-20 gap-4 max-w-[1024px] min-h-screen font-[family-name:var(--font-geist-sans)]"
      >
        <div className="mb-8 text-gray-600">
          Welcome to Recipe Board! Please tell us your name and your favorite
          food.
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="name" className="font-semibold text-sm">
            Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            className="border border-gray-400 p-2 rounded"
          />
        </div>
        <div className="flex flex-col gap-1 mb-4">
          <label htmlFor="favorite-food" className="font-semibold text-sm">
            Favorite Food
          </label>
          <fieldset className="grid grid-cols-3 gap-2">
            {FOOD_OPTIONS.map((food) => (
              <div
                key={food.toLowerCase()}
                className="h-12 flex flex-row items-center w-full"
              >
                <input
                  type="radio"
                  id={food.toLowerCase()}
                  value={food.toLowerCase()}
                  name="favorite-food"
                  className="peer appearance-none"
                />
                <label
                  htmlFor={food.toLowerCase()}
                  className="border w-full text-center border-gray-300 hover:border-gray-500 p-2 rounded peer-checked:border-black cursor-pointer"
                >
                  {food}
                </label>
              </div>
            ))}
          </fieldset>
        </div>
        <RegisterButton />
      </form>
    </div>
  );
};

export default async function Home() {
  const cookieStore = await cookies();
  const userIdEntry = cookieStore.get(USER_ID_COOKIE_KEY);
  if (userIdEntry) {
    const userId = userIdEntry.value;
    return <RecipeFeed userId={userId} />;
  } else {
    return <RegisterUser />;
  }
}
