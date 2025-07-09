
import { tool } from "ai";
import { postEntryGroupsDataSchema } from "./aitm.schema.ts";
import { postEntryGroups, PostEntryGroupsData } from "..";

export default tool({
  description: `
  Post an entry
Create a new entry in a discussion topic. Returns a json representation of
the created
entry (see documentation for 'entries' method) on success.
    `,
  parameters: postEntryGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<PostEntryGroupsData, "url"> ) => {
    try {
      const { data } = await postEntryGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    