
import { tool } from "ai";
import { listMembersOfCollaborationDataSchema } from "./aitm.schema.ts";
import { listMembersOfCollaboration, ListMembersOfCollaborationData } from "..";

export default tool({
  description: `
  List members of a collaboration.
A paginated list of the collaborators of a given collaboration
    `,
  parameters: listMembersOfCollaborationDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMembersOfCollaborationData, "url"> ) => {
    try {
      const { data } = await listMembersOfCollaboration(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    