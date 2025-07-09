
import { tool } from "ai";
import { setOrRemoveRestrictionsOnBlueprintCourseObjectDataSchema } from "./aitm.schema.ts";
import { setOrRemoveRestrictionsOnBlueprintCourseObject, SetOrRemoveRestrictionsOnBlueprintCourseObjectData } from "..";

export default tool({
  description: `
  Set or remove restrictions on a blueprint course object
If a blueprint course object is restricted,
editing will be limited for copies in associated courses.
    `,
  parameters: setOrRemoveRestrictionsOnBlueprintCourseObjectDataSchema.omit({ url: true }),
  execute: async (args : Omit<SetOrRemoveRestrictionsOnBlueprintCourseObjectData, "url"> ) => {
    try {
      const { data } = await setOrRemoveRestrictionsOnBlueprintCourseObject(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    