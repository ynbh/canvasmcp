
import { tool } from "ai";
import { getSingleUserLtiDataSchema } from "./aitm.schema.ts";
import { getSingleUserLti, GetSingleUserLtiData } from "..";

export default tool({
  description: `
  Get a single user (lti)
Get a single Canvas user by Canvas id or LTI id. Tool providers may only
access
users that have been assigned an assignment associated with their tool.
    `,
  parameters: getSingleUserLtiDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleUserLtiData, "url"> ) => {
    try {
      const { data } = await getSingleUserLti(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    