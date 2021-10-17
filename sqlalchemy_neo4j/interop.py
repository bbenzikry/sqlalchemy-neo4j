import os
import jpype


def start_jvm(initial_class_path=None, *additional_args):
    # Load JVM upfront. This
    args = "-Djava.class.path=%s" % (
        initial_class_path if initial_class_path else os.environ.get("CLASSPATH")
    )
    if len(additional_args) > 0:
        args = f"{args}{' '.join(additional_args)}"
    jvm_path = jpype.getDefaultJVMPath()
    jpype.startJVM(jvm_path, args)
    return jvm_path


def set_classpath(class_path):
    os.environ["CLASSPATH"] = class_path
