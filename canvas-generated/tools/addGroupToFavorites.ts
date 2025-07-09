
import { tool } from "ai";
import { addGroupToFavoritesDataSchema } from "./aitm.schema.ts";
import { addGroupToFavorites, AddGroupToFavoritesData } from "..";

export default tool({
  description: `
  Add group to favorites
Add a group to the current user's favorites.  If the group is already
in the
user's favorites, nothing happens.
    `,
  parameters: addGroupToFavoritesDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddGroupToFavoritesData, "url"> ) => {
    try {
      const { data } = await addGroupToFavorites(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    