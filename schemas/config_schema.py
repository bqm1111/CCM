"""One should use DsAppConfig, VideoConfig, MOT_sgie_config, FACE_sgie_config, parse_txt_as"""
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple, Type, TypeVar

from pydantic import (AnyHttpUrl, AnyUrl, BaseModel, DirectoryPath, Field,
                      NonNegativeFloat, NonNegativeInt, PositiveFloat,
                      PositiveInt, StrBytes, constr, parse_obj_as)

import sys
sys.path.append("../")

from schemas.datatype import (BoolEnum, ClusterMode, DsAppType, EncodeType,
                             ModelColorFormat, NetworkMode, NetworkType,
                             ProcessMode, TensorDataType)


class DsAppConfig(BaseModel):
    """Config for deepstream app"""

    app_type: DsAppType = DsAppType.NORMAL
    face_raw_meta_topic: str = "RawFaceMeta"
    mot_raw_meta_topic: str = "RawMotMeta"
    visual_topic: str = "RawImage"
    kafka_connection_str: str
    streammux_output_width: PositiveInt = 3840
    streammux_output_height: PositiveInt = 2160
    streammux_batch_size: PositiveInt
    streammux_buffer_pool: PositiveInt = 40
    streammux_nvbuf_memory_type: NonNegativeInt = 3
    face_confidence_threshold: PositiveFloat = 0.45
    mot_confidence_threshold: PositiveFloat = 0.45
    gpu_id: int = 0


class SingleSourceConfig(BaseModel):
    """properties of a single video source"""

    camera_id: str
    address: AnyUrl
    encode_type: EncodeType = EncodeType.H265
    type: str = Field("rtsp", const=True)
    stream: bool = False


class SourcesConfig(BaseModel):
    """
    info of rtsp streams
    """

    sources: List[SingleSourceConfig] = Field([], description="list of information of all rtsp streams")


class NVinferConfig(BaseModel):
    __input_tensor_meta__: bool = Field(False, description="This is GST properties, not a configuration key")
    gie_unique_id: NonNegativeInt
    gpu_id: NonNegativeInt
    network_mode: NetworkMode = NetworkMode.FP16
    model_engine_file: Path
    net_scale_factor: Optional[PositiveFloat] = 1
    custom_lib_path: Optional[Path]
    parse_bbox_func_name: Optional[str]
    offsets: Optional[constr(regex=r"^[\d\.;]*$")] = Field(
        description="Semicolon delimited float array, all values ≥0"
    )
    model_color_format: Optional[ModelColorFormat]
    infer_dims: Optional[constr(regex=r"^[\d;]*$")]
    interval: Optional[NonNegativeInt] = Field(
        description="Specifies the number of consecutive batches to be skipped for inference"
    )

class PGIEConfig(NVinferConfig):
    """PGIE property"""

    batch_size: PositiveInt
    labelfile_path: Path
    num_detected_classes: PositiveInt
    output_blob_names: Optional[str]
    cluster_mode: ClusterMode = ClusterMode.NMS
    maintain_aspect_ratio: NonNegativeInt = Field(1, const=True)
    process_mode: PositiveInt = Field(1, const=True)
    symmetric_padding: NonNegativeInt = Field(1, const=True)
    network_type: NetworkType = Field(NetworkType.DETECTOR, const=True)

    """PGIE class-attrs-all"""
    nms_iou_threshold: PositiveFloat = 0.5
    pre_cluster_threshold: PositiveFloat = 0.4

    def __str__(self) -> str:
        data = "[property]\n"
        for key, value in self.dict().items():
            if value is not None and key not in [
                "nms_iou_threshold",
                "pre_cluster_threshold",
                "post_cluster_threshold",
            ]:
                data += f"{key.replace('_', '-')}={value}\n"
        data += "\n\n"
        data += "[class-attrs-all]\n"
        for key, value in self.dict().items():
            if value is not None and key in ["nms_iou_threshold", "pre_cluster_threshold", "post_cluster_threshold"]:
                data += f"{key.replace('_', '-')}={value}\n"
        data += "\n"
        return data


class SGIEConfig(NVinferConfig):
    """SGIE property"""

    process_mode: int = Field(2, const=True, description="1=Primary, 2=Secondary")
    output_tensor_meta: int = Field(1, description="for our application, always 1", const=True)
    process_mode: ProcessMode = Field(ProcessMode.SECONDARY, const=True)
    network_type: Optional[NetworkType]
    batch_size: PositiveInt

    def __str__(self) -> str:
        data = "[property]\n"
        for key, value in self.dict().items():
            if value is None:
                continue
            data += f"{key.replace('_', '-')}={value}\n"
        data += "\n"
        return data


class MOT_pgie_config(PGIEConfig):
    gie_unique_id: NonNegativeInt = Field(1, const=True)
    num_detected_classes: PositiveInt = 2
    output_blob_names: str = "output"
    parse_bbox_func_name: str = Field("NvDsInferParseCustomYoloV5", const=True)
    model_color_format: ModelColorFormat = ModelColorFormat.RGB
    net_scale_factor: PositiveFloat = 0.0039215697906911373


class FACE_pgie_config(PGIEConfig):
    gie_unique_id: NonNegativeInt = Field(3, const=True)
    num_detected_classes: PositiveInt = 1
    cluster_mode: ClusterMode = Field(ClusterMode.NONE, const=True)
    parse_bbox_func_name: str = Field("NvDsInferParseNone", const=True)
    engine_create_func_name: str = Field("NvDsInferRetinafaceCudaEngineGet", const=True)
    offsets: Optional[constr(regex=r"^[\d\.;]*$")] = "104.0;117.0;123.0"
    model_color_format: ModelColorFormat = ModelColorFormat.BGR
    # net_scale_factor: PositiveFloat = 0.0039215697906911373
    infer_dims: Optional[constr(regex=r"^[\d;]*$")] = "3;736;1280"
    nms_iou_threshold: PositiveFloat = 0.4
    pre_cluster_threshold: PositiveFloat = 0.1
    post_cluster_threshold: PositiveFloat = 0.7


class MOT_sgie_config(SGIEConfig):
    gie_unique_id: NonNegativeInt = Field(2, const=True)
    input_object_min_width: NonNegativeInt = 0
    input_object_min_height: NonNegativeInt = 0
    operate_on_gie_id: NonNegativeInt = Field(1, const=True)
    operate_on_class_ids: NonNegativeInt = Field(0, const=True)
    output_blob_names: str = "output.0"
    output_tensor_meta: BoolEnum = Field(BoolEnum.TRUE, const=True)
    force_implicit_batch_dim: BoolEnum = BoolEnum.TRUE
    model_color_format: ModelColorFormat = Field(ModelColorFormat.BGR, const=True)
    classifier_async_mode: BoolEnum = BoolEnum.FALSE
    classifier_threshold: NonNegativeFloat = 0.0
    maintain_aspect_ratio: BoolEnum = BoolEnum.FALSE
    secondary_reinfer_interval: NonNegativeInt = 0
    net_scale_factor: PositiveFloat = Field(0.0039215697906911373)
    infer_dims: constr(regex=r"^[\d;]*$") = Field("3;128;64")
    network_type: NetworkType = Field(NetworkType.CLASSIFIER, const=True)


class FACE_sgie_config(SGIEConfig):
    gie_unique_id: NonNegativeInt = Field(4, const=True)
    output_tensor_meta: NonNegativeInt = Field(1, const=True)
    cluster_mode: ClusterMode = Field(ClusterMode.NONE, const=True)


class FACE_align_config(BaseModel):
    enable: NonNegativeInt = Field(1, const=True)
    gpu_id: NonNegativeInt
    target_unique_ids: NonNegativeInt = Field(4, const=True, description="match the gie-unique-id of the faceid sgie")
    network_input_shape: constr(regex=r"^[\d;]*$") = Field("32;3;112;112")
    tensor_data_type: TensorDataType = Field(TensorDataType.FP32, const=True)
    tensor_buf_pool_size: NonNegativeInt = 10  # preallocate 10*network-input-shape*tensor-data-type
    input_object_min_width: NonNegativeInt = 50
    input_object_max_width: NonNegativeInt = 3840
    input_object_min_height: NonNegativeInt = 50
    input_object_max_height: NonNegativeInt = 2160
    tensor_name: str = Field("conv1", const=True)

    def __str__(self) -> str:
        data = "[property]\n"
        for key, value in self.dict().items():
            data += f"{key.replace('_', '-')}={value}\n"
        data += "\n"
        return data


class DsInstanceConfig(BaseModel):
    appconfig: DsAppConfig
    sourceconfig: SourcesConfig
    mot_pgie: MOT_pgie_config
    face_pgie: FACE_pgie_config
    mot_sgie: MOT_sgie_config
    face_sgie: FACE_sgie_config
    face_align: FACE_align_config
        

T = TypeVar("T")


def parse_txt_as(type_: Type[T], b: StrBytes) -> Tuple[str, T]:
    matchlist = re.findall(r"^(?P<key>[a-z\-]+)=(?P<value>[^#\s]*)(?P<comment>[^\n]*#*.*)$", b, re.MULTILINE)
    argdict = {}
    for match in matchlist:
        argdict[match[0].replace("-", "_")] = match[1]
        
    return argdict, parse_obj_as(type_, argdict)


def write_config(
    path: DirectoryPath,
    instance_config: DsInstanceConfig
):
    """write app_conf as well as all network configurations"""
    if not os.path.exists(path):
        os.makedirs(path)
        
    with open(os.path.join(path, "app_conf.json"), "w") as f:
        f.write(instance_config.appconfig.json(indent=4))

    with open(os.path.join(path, "source_list.json"), "w") as f:
        f.write(instance_config.sourceconfig.json(indent=4))

    with open(os.path.join(path, "mot_primary.txt"), "w") as f:
        f.write(str(instance_config.mot_pgie))

    with open(os.path.join(path, "faceid_primary.txt"), "w") as f:
        f.write(str(instance_config.face_pgie))

    with open(os.path.join(path, "mot_sgie.txt"), "w") as f:
        f.write(str(instance_config.mot_sgie))

    with open(os.path.join(path, "faceid_secondary.txt"), "w") as f:
        f.write(str(instance_config.face_sgie))

    with open(os.path.join(path, "faceid_align_config.txt"), "w") as f:
        f.write(str(instance_config.face_align))


def __write_test():
    appconfig = DsAppConfig(kafka_connection_str="tainp.local:9092", streammux_batch_size=1)

    source = SourcesConfig(
        sources=[
            SingleSourceConfig(camera_id=3, address="rtsp://admin:123456a%40@172.21.111.101/main"),
            SingleSourceConfig(camera_id=1, address="rtsp://admin:123456a%40@172.21.111.104/main"),
            SingleSourceConfig(camera_id=2, address="rtsp://admin:123456a%40@172.21.111.111/main"),
            SingleSourceConfig(camera_id=4, address="rtsp://admin:123456a%40@172.21.104.112/main"),
        ]
    )

    mot_pgie = MOT_pgie_config(
        gpu_id=0,
        batch_size=len(source.sources),
        model_engine_file="../data/models/trt/deepsort_detector.trt",
        labelfile_path="../data/labels/mot_pgie_labels.txt",
        custom_lib_path="../build/src/nvdsinfer_customparser/libnvds_infercustomparser.so",
    )
    
    face_pgie = FACE_pgie_config(
        gpu_id=0,
        batch_size=len(source.sources),
        model_engine_file="../build/model_b24_gpu0_fp16.engine",
        labelfile_path="../data/labels/face_labels.txt",
        custom_lib_path="../build/src/facedetection/libnvds_facedetection.so",
    )

    mot_sgie = MOT_sgie_config(
        gpu_id=0,
        batch_size=12,
        model_engine_file="../data/models/trt/deepsort_extractor.trt",
    )

    face_sgie = FACE_sgie_config(
        gpu_id=0,
        batch_size=32,
        model_engine_file="../data/models/trt/glint360k_r50.trt",
        custom_lib_path="../build/src/facefeature/libnvds_parsenone.so",
        parse_bbox_func_name="NvDsInferParseNone",
    )

    face_align = FACE_align_config(
        tensor_buf_pool_size=10,
        input_object_min_width=50,
        input_object_max_width=3840,
        input_object_min_height=50,
        input_object_max_height=2160,
    )
    
    instance_config = DsInstanceConfig(
        appconfig=appconfig,
        sourceconfig=source,
        mot_pgie=mot_pgie,
        face_pgie=face_pgie,
        mot_sgie=mot_sgie,
        face_sgie=face_sgie,
        face_align=face_align
    )

    write_config(".", instance_config)


def __parse_test():
    with open("faceid_primary.txt") as f:
        face_pgie, a = parse_txt_as(FACE_pgie_config, f.read())
        print(face_pgie)
    with open("mot_primary.txt") as f:
        _, a = parse_txt_as(MOT_pgie_config, f.read())

    with open("faceid_secondary.txt") as f:
        _, a = parse_txt_as(FACE_sgie_config, f.read())

    with open("mot_sgie_copy.txt") as f:
        _, a = parse_txt_as(MOT_sgie_config, f.read())

    with open("faceid_align_config.txt") as f:
        _, a = parse_txt_as(FACE_align_config, f.read())


if __name__ == "__main__":
    # __write_test()
    __parse_test()
