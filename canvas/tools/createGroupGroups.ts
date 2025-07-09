
import { tool } from "ai";
import { createGroupGroupsDataSchema } from "./aitm.schema.ts";
import { createGroupGroups, CreateGroupGroupsData } from "..";

export default tool({
  description: `
  Create a group
Creates a new group. Groups created using the "/api/v1/groups/"
endpoint will be
community groups.
    `,
  parameters: createGroupGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateGroupGroupsData, "url"> ) => {
    try {
      const { data } = await createGroupGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    