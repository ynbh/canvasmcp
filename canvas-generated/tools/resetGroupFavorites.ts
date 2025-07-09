
import { tool } from "ai";
import { resetGroupFavoritesDataSchema } from "./aitm.schema.ts";
import { resetGroupFavorites, ResetGroupFavoritesData } from "..";

export default tool({
  description: `
  Reset group favorites
Reset the current user's group favorites to the default
automatically
generated list of enrolled group
    `,
  parameters: resetGroupFavoritesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ResetGroupFavoritesData, "url"> ) => {
    try {
      const { data } = await resetGroupFavorites(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    