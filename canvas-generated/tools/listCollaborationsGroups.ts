
import { tool } from "ai";
import { listCollaborationsGroupsDataSchema } from "./aitm.schema.ts";
import { listCollaborationsGroups, ListCollaborationsGroupsData } from "..";

export default tool({
  description: `
  List collaborations
A paginated list of collaborations the current user has access to in the
context
of the course provided in the url. NOTE: this only returns
ExternalToolCollaboration type
collaborations.

curl https://<canvas>/api/v1/courses/1/collaborations/
    `,
  parameters: listCollaborationsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCollaborationsGroupsData, "url"> ) => {
    try {
      const { data } = await listCollaborationsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    