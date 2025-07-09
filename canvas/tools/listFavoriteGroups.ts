
import { tool } from "ai";
import { listFavoriteGroupsDataSchema } from "./aitm.schema.ts";
import { listFavoriteGroups, ListFavoriteGroupsData } from "..";

export default tool({
  description: `
  List favorite groups
Retrieve the paginated list of favorite groups for the current user. If the
user has not chosen
any favorites, then a selection of groups that the user is a member of will be
returned.
    `,
  parameters: listFavoriteGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListFavoriteGroupsData, "url"> ) => {
    try {
      const { data } = await listFavoriteGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    