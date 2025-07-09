
import { tool } from "ai";
import { removeCourseFromFavoritesDataSchema } from "./aitm.schema.ts";
import { removeCourseFromFavorites, RemoveCourseFromFavoritesData } from "..";

export default tool({
  description: `
  Remove course from favorites
Remove a course from the current user's favorites.
    `,
  parameters: removeCourseFromFavoritesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveCourseFromFavoritesData, "url"> ) => {
    try {
      const { data } = await removeCourseFromFavorites(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    