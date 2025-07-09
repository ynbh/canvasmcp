
import { tool } from "ai";
import { getUserProfileDataSchema } from "./aitm.schema.ts";
import { getUserProfile, GetUserProfileData } from "..";

export default tool({
  description: `
  Get user profile
Returns user profile data, including user id, name, and profile pic.

When
requesting the profile for the user accessing the API, the user's
calendar feed URL and LTI user id
will be returned as well.
    `,
  parameters: getUserProfileDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetUserProfileData, "url"> ) => {
    try {
      const { data } = await getUserProfile(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    