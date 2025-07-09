
import { tool } from "ai";
import { resetCourseFavoritesDataSchema } from "./aitm.schema.ts";
import { resetCourseFavorites, ResetCourseFavoritesData } from "..";

export default tool({
  description: `
  Reset course favorites
Reset the current user's course favorites to the default
automatically
generated list of enrolled courses
    `,
  parameters: resetCourseFavoritesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ResetCourseFavoritesData, "url"> ) => {
    try {
      const { data } = await resetCourseFavorites(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    