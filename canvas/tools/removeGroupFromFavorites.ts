
import { tool } from "ai";
import { removeGroupFromFavoritesDataSchema } from "./aitm.schema.ts";
import { removeGroupFromFavorites, RemoveGroupFromFavoritesData } from "..";

export default tool({
  description: `
  Remove group from favorites
Remove a group from the current user's favorites.
    `,
  parameters: removeGroupFromFavoritesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveGroupFromFavoritesData, "url"> ) => {
    try {
      const { data } = await removeGroupFromFavorites(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    