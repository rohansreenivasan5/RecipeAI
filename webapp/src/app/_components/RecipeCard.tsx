"use client";

import { useState } from "react";

export interface RecipeCardProps {
  recipe: Recipe;
  liked?: 0 | 1 | -1;
  onLike?: (id: number, like: 1 | -1) => Promise<void>;
}

export const RecipeCard = ({
  recipe: { id, title, directions, url },
  liked: initialLiked,
  onLike,
}: Readonly<RecipeCardProps>) => {
  const [liked, setLiked] = useState(initialLiked);
  return (
    <div
      key={id}
      className="flex flex-col bg-white rounded-lg shadow-lg overflow-hidden md:min-w-[300px] max-w-[300px] w-full border px-6 py-4 gap-2"
    >
      <a
        href={url}
        target="_blank"
        className="text-xl font-semibold hover:underline line-clamp-2"
      >
        {title}
      </a>
      <p className="text-gray-600 line-clamp-4 flex-grow">{directions}</p>
      <div className="flex gap-1 mt-2">
        {!liked && (
          <>
            <button
              className="hover:underline"
              onClick={async () => {
                await onLike?.(id, 1);
                setLiked(1);
              }}
            >
              like
            </button>
            |
            <button
              className="hover:underline"
              onClick={async () => {
                await onLike?.(id, -1);
                setLiked(-1);
              }}
            >
              dislike
            </button>
          </>
        )}
        {liked === 1 && <span>✅ Liked</span>}
        {liked === -1 && <span>❌ Disliked</span>}
      </div>
    </div>
  );
};
