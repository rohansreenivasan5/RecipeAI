const endpoint = "http://127.0.0.1:8000";

export const getRequest = async (url: string, params?: any) => {
  const fullPath = !params
    ? url
    : url + "?" + new URLSearchParams(params).toString();
  const response = await fetch(endpoint + fullPath);
  return response.json();
};

export const postRequest = async (url: string, data: any) => {
  const response = await fetch(endpoint + url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return response.json();
};

export const getRecipeFeed = async (userId: string, n: number) => {
  const { data } = await getRequest("/api/recipe/", { userId, n });
  return data as Recipe[];
};

export const getUserProfile = async (userId: string) => {
  const { data } = await getRequest(`/api/user/${userId}/`);
  return data as UserProfile;
};

export const updateUserPreference = async (
  userId: string,
  recipeId: number,
  like: 1 | -1
) => {
  await postRequest(`/api/user/${userId}/`, { recipeId, like });
};

export const registerUser = async (name: string, cuisine: string) => {
  const {
    data: { userId },
  } = await postRequest("/api/user/", { name, cuisine });
  return userId as string;
};
