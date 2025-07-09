
import { tool } from "ai";
import { addCourseToFavoritesDataSchema } from "./aitm.schema.ts";
import { addCourseToFavorites, AddCourseToFavoritesData } from "..";

export default tool({
  description: `
  Add course to favorites
Add a course to the current user's favorites.  If the course is already
in
the user's favorites, nothing happens.
    `,
  parameters: addCourseToFavoritesDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddCourseToFavoritesData, "url"> ) => {
    try {
      const { data } = await addCourseToFavorites(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    