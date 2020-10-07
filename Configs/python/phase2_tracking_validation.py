import FWCore.ParameterSet.Config as cms

def customise_common(process):

    #CPE
    process.PixelCPEGenericESProducer = cms.ESProducer('PixelCPEGenericESProducer',
            Alpha2Order = cms.bool(True),
            ClusterProbComputationFlag = cms.int32(0),
            ComponentName = cms.string('PixelCPEGeneric'),
            DoCosmics = cms.bool(False),
            DoLorentz = cms.bool(False),
            EdgeClusterErrorX = cms.double(50),
            EdgeClusterErrorY = cms.double(85),
            IrradiationBiasCorrection = cms.bool(False),
            LoadTemplatesFromDB = cms.bool(False),
            MagneticFieldRecord = cms.ESInputTag('',''),
            SmallPitch = cms.bool(False),
            TruncatePixelCharge = cms.bool(False),
            Upgrade = cms.bool(True),
            UseErrorsFromTemplates = cms.bool(False),
            appendToDataLabel = cms.string(''),
            eff_charge_cut_highX = cms.double(1),
            eff_charge_cut_highY = cms.double(1),
            eff_charge_cut_lowX = cms.double(0),
            eff_charge_cut_lowY = cms.double(0),
            inflate_all_errors_no_trk_angle = cms.bool(False),
            inflate_errors = cms.bool(False),
            lAOffset = cms.double(0),
            lAWidthBPix = cms.double(0),
            lAWidthFPix = cms.double(0),
            size_cutX = cms.double(3),
            size_cutY = cms.double(3),
            useLAAlignmentOffsets = cms.bool(False),
            useLAWidthFromDB = cms.bool(True)
        )

    #Region Definitions
    process.pixelTracksTrackingRegions = cms.EDProducer('GlobalTrackingRegionFromBeamSpotEDProducer',
        RegionPSet = cms.PSet(
            beamSpot = cms.InputTag('offlineBeamSpot'),
            nSigmaZ = cms.double(4.0),
            originRadius = cms.double(0.02),
            precise = cms.bool(True),
            ptMin = cms.double(0.9)
        )
    )
    process.initialStepTrackingRegions = process.pixelTracksTrackingRegions.clone()
    process.highPtTripletStepTrackingRegions = process.pixelTracksTrackingRegions.clone()

    #Seeding
    layerList = ['BPix1+BPix2+BPix3+BPix4',
            'BPix1+BPix2+BPix3+FPix1_pos',
            'BPix1+BPix2+BPix3+FPix1_neg',
            'BPix1+BPix2+FPix1_pos+FPix2_pos',
            'BPix1+BPix2+FPix1_neg+FPix2_neg',
            'BPix1+FPix1_pos+FPix2_pos+FPix3_pos',
            'BPix1+FPix1_neg+FPix2_neg+FPix3_neg',
            'FPix1_pos+FPix2_pos+FPix3_pos+FPix4_pos',
            'FPix1_neg+FPix2_neg+FPix3_neg+FPix4_neg',
            'FPix2_pos+FPix3_pos+FPix4_pos+FPix5_pos',
            'FPix2_neg+FPix3_neg+FPix4_neg+FPix5_neg',
            'FPix3_pos+FPix4_pos+FPix5_pos+FPix6_pos',
            'FPix3_neg+FPix4_neg+FPix5_neg+FPix6_neg',
            'FPix4_pos+FPix5_pos+FPix6_pos+FPix7_pos',
            'FPix4_neg+FPix5_neg+FPix6_neg+FPix7_neg',
            'FPix5_pos+FPix6_pos+FPix7_pos+FPix8_pos',
            'FPix5_neg+FPix6_neg+FPix7_neg+FPix8_neg']

    from RecoTracker.TkSeedingLayers.seedingLayersEDProducer_cfi import seedingLayersEDProducer

    #Seed Layers
    process.hittrack = cms.PSet(
        HitProducer = cms.string('siPixelRecHits'),
        TTRHBuilder = cms.string('WithTrackAngle')
    )

    process.pixelTracksSeedLayers = seedingLayersEDProducer.clone(
        BPix = process.hittrack,
        FPix = process.hittrack,
        layerList = cms.vstring(layerList)
    )

    process.initialStepSeedLayers = process.pixelTracksSeedLayers.clone()

    #Pixel Tracks
    from RecoTracker.TkHitPairs.hitPairEDProducerDefault_cfi import hitPairEDProducerDefault
    process.pixelTracksHitDoublets = hitPairEDProducerDefault.clone(
        produceIntermediateHitDoublets = cms.bool(True),
        produceSeedingHitSets = cms.bool(False),
        seedingLayers = cms.InputTag('pixelTracksSeedLayers'),
        trackingRegions = cms.InputTag('pixelTracksTrackingRegions'),
        )

    from RecoPixelVertexing.PixelTriplets.caHitQuadrupletEDProducer_cfi import caHitQuadrupletEDProducer
    process.pixelTracksHitQuadruplets = caHitQuadrupletEDProducer.clone(
        CAPhiCut = cms.double(0.2),
        CAThetaCut = cms.double(0.0012),
        SeedComparitorPSet = cms.PSet(
            ComponentName = cms.string('LowPtClusterShapeSeedComparitor'),
            clusterShapeCacheSrc = cms.InputTag('siPixelClusterShapeCache'),
            clusterShapeHitFilter = cms.string('ClusterShapeHitFilter')
        ),
        doublets = cms.InputTag('pixelTracksHitDoublets'),
        extraHitRPhitolerance = cms.double(0.032),
        fitFastCircle = cms.bool(True), ##TOD
        fitFastCircleChi2Cut = cms.bool(True),
        maxChi2 = cms.PSet(
            enabled = cms.bool(True),
            pt1 = cms.double(0.7),
            pt2 = cms.double(2.0),
            value1 = cms.double(200.0),
            value2 = cms.double(50.0)
        ),
        useBendingCorrection = cms.bool(True)
    )

    from RecoPixelVertexing.PixelTrackFitting.pixelTrackFilterByKinematics_cfi import pixelTrackFilterByKinematics
    process.pixelTrackFilterByKinematics = pixelTrackFilterByKinematics.clone(
        ptMin = cms.double(0.9),
    )

    process.load("RecoPixelVertexing.PixelTrackFitting.pixelFitterByHelixProjections_cfi")
    process.load("RecoPixelVertexing.PixelTrackFitting.pixelTrackCleanerBySharedHits_cfi")

    process.pixelTracks = cms.EDProducer('PixelTrackProducer',
        Cleaner = cms.string('pixelTrackCleanerBySharedHits'),
        Filter = cms.InputTag('pixelTrackFilterByKinematics'),
        Fitter = cms.InputTag('pixelFitterByHelixProjections'),
        SeedingHitSets = cms.InputTag('pixelTracksHitQuadruplets'),
        passLabel = cms.string('pixelTracks')
    )

    from RecoPixelVertexing.PixelVertexFinding.PixelVertexes_cfi import pixelVertices

    process.pixelVertices = pixelVertices.clone(
        PVcomparer = cms.PSet(refToPSet_ = cms.string('pSetPvClusterComparerForIT')),
        TrackCollection = cms.InputTag('pixelTracks'),
        ZOffset = cms.double(5.0),
        ZSeparation = cms.double(0.025),
    )

    process.pSetPvClusterComparerForIT = cms.PSet(
        track_chi2_max = cms.double( 50.0 ),
        track_pt_max = cms.double( 50.0 ),
        track_prob_min = cms.double( -1.0 ),
        track_pt_min = cms.double( 1.0 )
    )

    process.highPtTripletStepTrajectoryCleanerBySharedHits = cms.ESProducer('TrajectoryCleanerESProducer',
            ComponentName = cms.string('highPtTripletStepTrajectoryCleanerBySharedHits'),
            ComponentType = cms.string('TrajectoryCleanerBySharedHits'),
            MissingHitPenalty = cms.double(20.0),
            ValidHitBonus = cms.double(5.0),
            allowSharedFirstHit = cms.bool(True),
            fractionShared = cms.double(0.16)
        )

    process.ak4CaloJetsForTrk = cms.EDProducer('FastjetJetProducer',
            doPVCorrection = cms.bool(True),
            inputEMin = cms.double(0.0),
            inputEtMin = cms.double(0.3),
            jetType = cms.string('CaloJet'),
            src = cms.InputTag('caloTowerForTrk'),
            srcPVs = cms.InputTag('firstStepPrimaryVerticesUnsorted'),
            useDeterministicSeed = cms.bool(True),
        )
    #Initia Step
    from RecoTracker.CkfPattern.GroupedCkfTrajectoryBuilder_cfi import GroupedCkfTrajectoryBuilder

    process.initialStepTrajectoryBuilder = GroupedCkfTrajectoryBuilder.clone(
            alwaysUseInvalidHits = cms.bool(False),
            estimator = cms.string('initialStepChi2Est'),
            inOutTrajectoryFilter = cms.PSet(
                refToPSet_ = cms.string('initialStepTrajectoryFilter')
            ),
            keepOriginalIfRebuildFails = cms.bool(True),
            maxCand = cms.int32(2),
            maxDPhiForLooperReconstruction = cms.double(2.0),
            maxPtForLooperReconstruction = cms.double(0.7),
            minNrOfHitsForRebuild = cms.int32(1),
            propagatorAlong = cms.string('PropagatorWithMaterialParabolicMf'),
            propagatorOpposite = cms.string('PropagatorWithMaterialParabolicMfOpposite'),

            trajectoryFilter = cms.PSet(
                refToPSet_ = cms.string('initialStepTrajectoryFilter')
            ),
        )


    process.highPtTripletStepTrajectoryBuilder = process.initialStepTrajectoryBuilder.clone(
        bestHitOnly = cms.bool(True),
        estimator = cms.string('highPtTripletStepChi2Est'),
        inOutTrajectoryFilter = cms.PSet(
            refToPSet_ = cms.string('highPtTripletStepTrajectoryFilterInOut')
        ),
        minNrOfHitsForRebuild = cms.int32(5),
        trajectoryFilter = cms.PSet(
            refToPSet_ = cms.string('highPtTripletStepTrajectoryFilter')
        ),
        useSameTrajFilter = cms.bool(False)
    )


    from RecoTracker.MeasurementDet.Chi2ChargeMeasurementEstimator_cfi import Chi2ChargeMeasurementEstimator

    process.initialStepChi2Est = Chi2ChargeMeasurementEstimator.clone(
        ComponentName = cms.string('initialStepChi2Est'),
        MaxChi2 = cms.double(9.0),
        MaxDisplacement = cms.double(0.5),
        MaxSagitta = cms.double(2),
        MinPtForHitRecoveryInGluedDet = cms.double(1000000.0),
        MinimalTolerance = cms.double(0.5),
        appendToDataLabel = cms.string(''),
        clusterChargeCut = cms.PSet(
            refToPSet_ = cms.string('SiStripClusterChargeCutLoose')
        ),
        nSigma = cms.double(3.0),
        pTChargeCutThreshold = cms.double(15.0)
    )

    process.highPtTripletStepChi2Est = process.initialStepChi2Est.clone(
        ComponentName = cms.string('highPtTripletStepChi2Est'),
        MaxChi2 = cms.double(16.0),
    )

    from TrackingTools.TrajectoryFiltering.TrajectoryFilter_cff import CkfBaseTrajectoryFilter_block
    process.initialStepTrajectoryFilter = CkfBaseTrajectoryFilter_block.clone(
            maxLostHits = cms.int32(1),
	     maxLostHitsFraction = cms.double(999.0), # previous 0.1
            minHitsMinPt = cms.int32(4),
            minPt = cms.double(0.9),
            minimumNumberOfHits = cms.int32(4),
        )

    process.highPtTripletStepTrajectoryFilterInOut = CkfBaseTrajectoryFilter_block.clone(
            minimumNumberOfHits = cms.int32(4),
            nSigmaMinPt = cms.double(5.0),
            seedExtension = cms.int32(1),
	    seedPairPenalty = cms.int32(0),
            minPt = cms.double(0.9),
             maxLostHitsFraction = cms.double(999.0), # previous 0.1
	    maxNumberOfHits = cms.int32(100)
        )

    process.highPtTripletStepTrajectoryFilterBase = cms.PSet(
               ComponentType = cms.string('CkfBaseTrajectoryFilter'),
    chargeSignificance = cms.double(-1.0),
    constantValueForLostHitsFractionFilter = cms.double(1.0), # previous 2.0
    extraNumberOfHitsBeforeTheFirstLoop = cms.int32(4),
    maxCCCLostHits = cms.int32(0), # previous 9999
    maxConsecLostHits = cms.int32(1),
    maxLostHits = cms.int32(1), # previous 999
    maxLostHitsFraction = cms.double(999.0), # previous 0.1
    maxNumberOfHits = cms.int32(100),
    minGoodStripCharge = cms.PSet(
        refToPSet_ = cms.string('SiStripClusterChargeCutNone')
    ),
    minHitsMinPt = cms.int32(3),
    minNumberOfHitsForLoopers = cms.int32(13),
    minNumberOfHitsPerLoop = cms.int32(4),
    minPt = cms.double(0.9), # ptcut previous 0.2
    minimumNumberOfHits = cms.int32(3),
    nSigmaMinPt = cms.double(5.0),
    pixelSeedExtension = cms.bool(False),
    seedExtension = cms.int32(1), # previous 0
    seedPairPenalty = cms.int32(0),
    strictSeedExtension = cms.bool(False)
	      )

    process.highPtTripletStepTrajectoryFilter = cms.PSet(
        ComponentType = cms.string('CompositeTrajectoryFilter'),
        filters = cms.VPSet(
            cms.PSet(
                refToPSet_ = cms.string('highPtTripletStepTrajectoryFilterBase')
            ),
            cms.PSet(
                refToPSet_ = cms.string('ClusterShapeTrajectoryFilter')
            )
        )
    )


    from RecoTracker.CkfPattern.CkfTrackCandidates_cfi import ckfTrackCandidates

    process.initialStepTrackCandidates = ckfTrackCandidates.clone(

        SimpleMagneticField = cms.string('ParabolicMf'),
        TrajectoryBuilderPSet = cms.PSet(
            refToPSet_ = cms.string('initialStepTrajectoryBuilder')
        ),
        maxNSeeds = cms.uint32(100000),
        maxSeedsBeforeCleaning = cms.uint32(1000),
        numHitsForSeedCleaner = cms.int32(50),
        onlyPixelHitsForSeedCleaner = cms.bool(True),
        src = cms.InputTag('initialStepSeeds'),
        useHitsSplitting = cms.bool(False)
    )

    process.highPtTripletStepTrackCandidates = ckfTrackCandidates.clone(
	ComponentType = cms.string('ckfTrackCandidates'),
        TrajectoryBuilderPSet = cms.PSet(
            refToPSet_ = cms.string('highPtTripletStepTrajectoryBuilder')
        ),
        TrajectoryCleaner = cms.string('highPtTripletStepTrajectoryCleanerBySharedHits'),

        phase2clustersToSkip = cms.InputTag('highPtTripletStepClusters'),
        src = cms.InputTag('highPtTripletStepSeeds'),


        maxNSeeds = cms.uint32(100000),
        maxSeedsBeforeCleaning = cms.uint32(1000),
        numHitsForSeedCleaner = cms.int32(50),
        onlyPixelHitsForSeedCleaner = cms.bool(True),
        useHitsSplitting = cms.bool(False)
    )


    process.highPtTripletStepSeeds = cms.EDProducer('SeedCreatorFromRegionConsecutiveHitsEDProducer',
        MinOneOverPtError = cms.double(1),
        OriginTransverseErrorMultiplier = cms.double(1),
        SeedComparitorPSet = cms.PSet(
            ComponentName = cms.string('none')
        ),
        SeedMomentumForBOFF = cms.double(5),
        TTRHBuilder = cms.string('WithTrackAngle'),
        forceKinematicWithRegionDirection = cms.bool(False),
        magneticField = cms.string(''),
        propagator = cms.string('PropagatorWithMaterial'),
        seedingHitSets = cms.InputTag('highPtTripletStepHitTriplets')
    )

    from RecoTracker.TrackProducer.TrackProducer_cfi import TrackProducer

    process.initialStepTracks = TrackProducer.clone(
        AlgorithmName = cms.string('initialStep'),
        Fitter = cms.string('FlexibleKFFittingSmoother'),
        TTRHBuilder = cms.string('WithTrackAngle'),
        src = cms.InputTag('initialStepTrackCandidates'),
        useHitsSplitting = cms.bool(False),
    )

    process.initialStepTrackRefsForJets = cms.EDProducer('ChargedRefCandidateProducer',
        particleType = cms.string('pi+'),
        src = cms.InputTag('initialStepTracks')
    )

    process.highPtTripletStepClusters = cms.EDProducer('TrackClusterRemoverPhase2',
        TrackQuality = cms.string('highPurity'),
        maxChi2 = cms.double(9.0),
        mightGet = cms.optional.untracked.vstring,
        minNumberOfLayersWithMeasBeforeFiltering = cms.int32(0),
        oldClusterRemovalInfo = cms.InputTag(''),
        overrideTrkQuals = cms.InputTag(''),
        phase2OTClusters = cms.InputTag('siPhase2Clusters'),
        phase2pixelClusters = cms.InputTag('siPixelClusters'),
        trackClassifier = cms.InputTag('','QualityMasks'),
        trajectories = cms.InputTag('initialStepTracksSelectionHighPurity')
    )

    process.highPtTripletStepSeedLayers = cms.EDProducer('SeedingLayersEDProducer',
        BPix = cms.PSet(
            HitProducer = cms.string('siPixelRecHits'),
            TTRHBuilder = cms.string('WithTrackAngle'),
            skipClusters = cms.InputTag('highPtTripletStepClusters')
        ),
        FPix = cms.PSet(
            HitProducer = cms.string('siPixelRecHits'),
            TTRHBuilder = cms.string('WithTrackAngle'),
            skipClusters = cms.InputTag('highPtTripletStepClusters')
        ),
        MTEC = cms.PSet(

        ),
        MTIB = cms.PSet(

        ),
        MTID = cms.PSet(

        ),
        MTOB = cms.PSet(

        ),
        TEC = cms.PSet(

        ),
        TIB = cms.PSet(

        ),
        TID = cms.PSet(

        ),
        TOB = cms.PSet(

        ),
        layerList = cms.vstring(
            'BPix1+BPix2+BPix3',
            'BPix2+BPix3+BPix4',
            'BPix1+BPix3+BPix4',
            'BPix1+BPix2+BPix4',
            'BPix2+BPix3+FPix1_pos',
            'BPix2+BPix3+FPix1_neg',
            'BPix1+BPix2+FPix1_pos',
            'BPix1+BPix2+FPix1_neg',
            'BPix2+FPix1_pos+FPix2_pos',
            'BPix2+FPix1_neg+FPix2_neg',
            'BPix1+FPix1_pos+FPix2_pos',
            'BPix1+FPix1_neg+FPix2_neg',
            'FPix1_pos+FPix2_pos+FPix3_pos',
            'FPix1_neg+FPix2_neg+FPix3_neg',
            'BPix1+FPix2_pos+FPix3_pos',
            'BPix1+FPix2_neg+FPix3_neg',
            'FPix2_pos+FPix3_pos+FPix4_pos',
            'FPix2_neg+FPix3_neg+FPix4_neg',
            'FPix3_pos+FPix4_pos+FPix5_pos',
            'FPix3_neg+FPix4_neg+FPix5_neg',
            'FPix4_pos+FPix5_pos+FPix6_pos',
            'FPix4_neg+FPix5_neg+FPix6_neg',
            'FPix5_pos+FPix6_pos+FPix7_pos',
            'FPix5_neg+FPix6_neg+FPix7_neg',
            'FPix6_pos+FPix7_pos+FPix8_pos',
            'FPix6_neg+FPix7_neg+FPix8_neg'
        ),
        mightGet = cms.optional.untracked.vstring
    )

    process.highPtTripletStepHitDoublets = cms.EDProducer('HitPairEDProducer',
        clusterCheck = cms.InputTag('trackerClusterCheck'),
        layerPairs = cms.vuint32(0, 1),
        maxElement = cms.uint32(50000000),
        maxElementTotal = cms.uint32(50000000),
        mightGet = cms.optional.untracked.vstring,
        produceIntermediateHitDoublets = cms.bool(True),
        produceSeedingHitSets = cms.bool(False),
        seedingLayers = cms.InputTag('highPtTripletStepSeedLayers'),
        trackingRegions = cms.InputTag('highPtTripletStepTrackingRegions'),
        trackingRegionsSeedingLayers = cms.InputTag('')
    )

    process.highPtTripletStepHitTriplets = cms.EDProducer('CAHitTripletEDProducer',
        CAHardPtCut = cms.double(0.5),
        CAPhiCut = cms.double(0.06),
        CAThetaCut = cms.double(0.003),
        SeedComparitorPSet = cms.PSet(
            ComponentName = cms.string('LowPtClusterShapeSeedComparitor'),
            clusterShapeCacheSrc = cms.InputTag('siPixelClusterShapeCache'),
            clusterShapeHitFilter = cms.string('ClusterShapeHitFilter')
        ),
        doublets = cms.InputTag('highPtTripletStepHitDoublets'),
        extraHitRPhitolerance = cms.double(0.032),
        maxChi2 = cms.PSet(
            enabled = cms.bool(True),
            pt1 = cms.double(0.8),
            pt2 = cms.double(8),
            value1 = cms.double(100),
            value2 = cms.double(6)
        ),
        useBendingCorrection = cms.bool(True)
    )

    process.firstStepPrimaryVerticesUnsorted = cms.EDProducer('PrimaryVertexProducer',
        TkClusParameters = cms.PSet(
            TkDAClusParameters = cms.PSet(
                Tmin = cms.double(2.0),
                Tpurge = cms.double(2.0),
                Tstop = cms.double(0.5),
                coolingFactor = cms.double(0.6),
                d0CutOff = cms.double(3.0),
                dzCutOff = cms.double(3.0),
                uniquetrkweight = cms.double(0.8),
                vertexSize = cms.double(0.006),
                zmerge = cms.double(0.01)
            ),
            algorithm = cms.string('DA_vect')
        ),
        TkFilterParameters = cms.PSet(
            algorithm = cms.string('filter'),
            maxD0Significance = cms.double(4.0),
            maxEta = cms.double(4.0),
            maxNormalizedChi2 = cms.double(10.0),
            minPixelLayersWithHits = cms.int32(2),
            minPt = cms.double(0.9),
            minSiliconLayersWithHits = cms.int32(5),
            trackQuality = cms.string('any')
        ),
        TrackLabel = cms.InputTag('initialStepTracks'),
        beamSpotLabel = cms.InputTag('offlineBeamSpot'),
        verbose = cms.untracked.bool(False),
        vertexCollections = cms.VPSet(cms.PSet(
            algorithm = cms.string('AdaptiveVertexFitter'),
            chi2cutoff = cms.double(2.5),
            label = cms.string(''),
            maxDistanceToBeam = cms.double(1.0),
            minNdof = cms.double(0.0),
            useBeamConstraint = cms.bool(False)
        ))
    )

    process.firstStepPrimaryVertices = cms.EDProducer('RecoChargedRefCandidatePrimaryVertexSorter',
        assignment = cms.PSet(
            maxDistanceToJetAxis = cms.double(0.07),
            maxDtSigForPrimaryAssignment = cms.double(4.0),
            maxDxyForJetAxisAssigment = cms.double(0.1),
            maxDxyForNotReconstructedPrimary = cms.double(0.01),
            maxDxySigForNotReconstructedPrimary = cms.double(2),
            maxDzErrorForPrimaryAssignment = cms.double(0.05),
            maxDzForJetAxisAssigment = cms.double(0.1),
            maxDzForPrimaryAssignment = cms.double(0.1),
            maxDzSigForPrimaryAssignment = cms.double(5.0),
            maxJetDeltaR = cms.double(0.5),
            minJetPt = cms.double(25),
            preferHighRanked = cms.bool(False),
            useTiming = cms.bool(False)
        ),
        jets = cms.InputTag('ak4CaloJetsForTrk'),
        particles = cms.InputTag('initialStepTrackRefsForJets'),
        produceAssociationToOriginalVertices = cms.bool(False),
        produceNoPileUpCollection = cms.bool(False),
        producePileUpCollection = cms.bool(False),
        produceSortedVertices = cms.bool(True),
        qualityForPrimary = cms.int32(3),
        sorting = cms.PSet(

        ),
        trackTimeResoTag = cms.InputTag(''),
        trackTimeTag = cms.InputTag(''),
        usePVMET = cms.bool(True),
        vertices = cms.InputTag('firstStepPrimaryVerticesUnsorted')
    )

    process.highPtTripletStepTracks = cms.EDProducer('TrackProducer',
        AlgorithmName = cms.string('highPtTripletStep'),
        Fitter = cms.string('FlexibleKFFittingSmoother'),
        GeometricInnerState = cms.bool(False),
        MeasurementTracker = cms.string(''),
        MeasurementTrackerEvent = cms.InputTag('MeasurementTrackerEvent'),
        NavigationSchool = cms.string('SimpleNavigationSchool'),
        Propagator = cms.string('RungeKuttaTrackerPropagator'),
        SimpleMagneticField = cms.string('ParabolicMf'),
        TTRHBuilder = cms.string('WithTrackAngle'),
        TrajectoryInEvent = cms.bool(False),
        alias = cms.untracked.string('ctfWithMaterialTracks'),
        beamSpot = cms.InputTag('offlineBeamSpot'),
        clusterRemovalInfo = cms.InputTag(''),
        src = cms.InputTag('highPtTripletStepTrackCandidates'),
        useHitsSplitting = cms.bool(False),
        useSimpleMF = cms.bool(False)
    )

    process.highPtTripletStepTrackCutClassifier = cms.EDProducer('TrackCutClassifier',
        beamspot = cms.InputTag('offlineBeamSpot'),
        ignoreVertices = cms.bool(False),
        mva = cms.PSet(
            dr_par = cms.PSet(
                d0err = cms.vdouble(0.003, 0.003, 0.003),
                d0err_par = cms.vdouble(0.002, 0.002, 0.001),
                dr_exp = cms.vint32(4, 4, 4),
                dr_par1 = cms.vdouble(0.7, 0.6, 0.6),
                dr_par2 = cms.vdouble(0.6, 0.5, 0.45)
            ),
            dz_par = cms.PSet(
                dz_exp = cms.vint32(4, 4, 4),
                dz_par1 = cms.vdouble(0.8, 0.7, 0.7),
                dz_par2 = cms.vdouble(0.6, 0.6, 0.55)
            ),
            maxChi2 = cms.vdouble(9999.0, 9999.0, 9999.0),
            maxChi2n = cms.vdouble(2.0, 1.0, 0.8),
            maxDr = cms.vdouble(0.5, 0.03, 3.40282346639e+38),
            maxDz = cms.vdouble(0.5, 0.2, 3.40282346639e+38),
            maxDzWrtBS = cms.vdouble(3.40282346639e+38, 24.0, 15.0),
            maxLostLayers = cms.vint32(3, 3, 2),
            min3DLayers = cms.vint32(3, 3, 4),
            minLayers = cms.vint32(3, 3, 4),
            minNVtxTrk = cms.int32(3),
            minNdof = cms.vdouble(1e-05, 1e-05, 1e-05),
            minPixelHits = cms.vint32(0, 0, 3)
        ),
        qualityCuts = cms.vdouble(-0.7, 0.1, 0.7),
        src = cms.InputTag('highPtTripletStepTracks'),
        vertices = cms.InputTag('pixelVertices')
    )

    process.highPtTripletStepTracksSelectionHighPurity = cms.EDProducer('TrackCollectionFilterCloner',
        copyExtras = cms.untracked.bool(True),
        copyTrajectories = cms.untracked.bool(False),
        minQuality = cms.string('highPurity'),
        originalMVAVals = cms.InputTag('highPtTripletStepTrackCutClassifier','MVAValues'),
        originalQualVals = cms.InputTag('highPtTripletStepTrackCutClassifier','QualityMasks'),
        originalSource = cms.InputTag('highlPtTripletStepTracks')
    )

    process.trackAlgoPriorityOrder = cms.ESProducer('TrackAlgoPriorityOrderESProducer',
        ComponentName = cms.string('trackAlgoPriorityOrder'),
        algoOrder = cms.vstring(
            'initialStep',
            'highPtTripletStep'
        ),
        appendToDataLabel = cms.string('')
    )

    process.generalTracks = cms.EDProducer('TrackListMerger',
        Epsilon = cms.double(-0.001),
        FoundHitBonus = cms.double(5.0),
        LostHitPenalty = cms.double(5.0),
        MaxNormalizedChisq = cms.double(1000.0),
        MinFound = cms.int32(3),
        MinPT = cms.double(0.9),
        ShareFrac = cms.double(0.19),
        TrackProducers = cms.VInputTag('initialStepTrackSelectionHP', 'highPtTripletStepTracksSelectionHighPurity'),
        allowFirstHitShare = cms.bool(True),
        copyExtras = cms.untracked.bool(True),
        copyMVA = cms.bool(False),
        hasSelector = cms.vint32(0, 0),
        indivShareFrac = cms.vdouble(1.0, 1.0),
        makeReKeyedSeeds = cms.untracked.bool(False),
        newQuality = cms.string('confirmed'),
        selectedTrackQuals = cms.VInputTag(cms.InputTag('initialStepTrackSelectionHP'), cms.InputTag('highPtTripletStepTracksSelectionHighPurity')),
        setsToMerge = cms.VPSet(cms.PSet(
            pQual = cms.bool(True),
            tLists = cms.vint32(0, 1)
        )),
        trackAlgoPriorityOrder = cms.string('trackAlgoPriorityOrder'),
        writeOnlyTrkQuals = cms.bool(False)
    )

    process.unsortedOfflinePrimaryVertices = cms.EDProducer('PrimaryVertexProducer',
        TkClusParameters = cms.PSet(
            TkDAClusParameters = cms.PSet(
                Tmin = cms.double(2.0),
                Tpurge = cms.double(2.0),
                Tstop = cms.double(0.5),
                coolingFactor = cms.double(0.6),
                d0CutOff = cms.double(3.0),
                dzCutOff = cms.double(3.0),
                uniquetrkweight = cms.double(0.8),
                vertexSize = cms.double(0.006),
                zmerge = cms.double(0.01)
            ),
            algorithm = cms.string('DA_vect')
        ),
        TkFilterParameters = cms.PSet(
            algorithm = cms.string('filter'),
            maxD0Significance = cms.double(4.0),
            maxEta = cms.double(4.0),
            maxNormalizedChi2 = cms.double(10.0),
            minPixelLayersWithHits = cms.int32(2),
            minPt = cms.double(0.9),
            minSiliconLayersWithHits = cms.int32(5),
            trackQuality = cms.string('any')
        ),
        TrackLabel = cms.InputTag('generalTracks'),
        beamSpotLabel = cms.InputTag('offlineBeamSpot'),
        verbose = cms.untracked.bool(False),
        vertexCollections = cms.VPSet(
            cms.PSet(
                algorithm = cms.string('AdaptiveVertexFitter'),
                chi2cutoff = cms.double(2.5),
                label = cms.string(''),
                maxDistanceToBeam = cms.double(1.0),
                minNdof = cms.double(0.0),
                useBeamConstraint = cms.bool(False)
            ),
            cms.PSet(
                algorithm = cms.string('AdaptiveVertexFitter'),
                chi2cutoff = cms.double(2.5),
                label = cms.string('WithBS'),
                maxDistanceToBeam = cms.double(1.0),
                minNdof = cms.double(2.0),
                useBeamConstraint = cms.bool(True)
            )
        )
    )

    process.trackWithVertexRefSelectorBeforeSorting = cms.EDProducer('TrackWithVertexRefSelector',
        copyExtras = cms.untracked.bool(False),
        copyTrajectories = cms.untracked.bool(False),
        d0Max = cms.double(999.0),
        dzMax = cms.double(999.0),
        etaMax = cms.double(5.0),
        etaMin = cms.double(0.0),
        nSigmaDtVertex = cms.double(0),
        nVertices = cms.uint32(0),
        normalizedChi2 = cms.double(999999.0),
        numberOfLostHits = cms.uint32(999),
        numberOfValidHits = cms.uint32(0),
        numberOfValidPixelHits = cms.uint32(0),
        ptErrorCut = cms.double(9e+99),
        ptMax = cms.double(9e+99),
        ptMin = cms.double(0.9),
        quality = cms.string('highPurity'),
        rhoVtx = cms.double(0.2),
        src = cms.InputTag('generalTracks'),
        timeResosTag = cms.InputTag(''),
        timesTag = cms.InputTag(''),
        useVtx = cms.bool(True),
        vertexTag = cms.InputTag('unsortedOfflinePrimaryVertices'),
        vtxFallback = cms.bool(True),
        zetaVtx = cms.double(1.0)
    )

    process.trackRefsForJetsBeforeSorting = cms.EDProducer('ChargedRefCandidateProducer',
        particleType = cms.string('pi+'),
        src = cms.InputTag('trackWithVertexRefSelectorBeforeSorting')
    )

    process.offlinePrimaryVerticesWithBS = cms.EDProducer('RecoChargedRefCandidatePrimaryVertexSorter',
        assignment = cms.PSet(
            maxDistanceToJetAxis = cms.double(0.07),
            maxDtSigForPrimaryAssignment = cms.double(4.0),
            maxDxyForJetAxisAssigment = cms.double(0.1),
            maxDxyForNotReconstructedPrimary = cms.double(0.01),
            maxDxySigForNotReconstructedPrimary = cms.double(2),
            maxDzErrorForPrimaryAssignment = cms.double(0.05),
            maxDzForJetAxisAssigment = cms.double(0.1),
            maxDzForPrimaryAssignment = cms.double(0.1),
            maxDzSigForPrimaryAssignment = cms.double(5.0),
            maxJetDeltaR = cms.double(0.5),
            minJetPt = cms.double(25),
            preferHighRanked = cms.bool(False),
            useTiming = cms.bool(False)
        ),
        jets = cms.InputTag('ak4CaloJetsForTrk'),
        particles = cms.InputTag('trackRefsForJetsBeforeSorting'),
        produceAssociationToOriginalVertices = cms.bool(False),
        produceNoPileUpCollection = cms.bool(False),
        producePileUpCollection = cms.bool(False),
        produceSortedVertices = cms.bool(True),
        qualityForPrimary = cms.int32(3),
        sorting = cms.PSet(

        ),
        trackTimeResoTag = cms.InputTag(''),
        trackTimeTag = cms.InputTag(''),
        usePVMET = cms.bool(True),
        vertices = cms.InputTag('unsortedOfflinePrimaryVertices','WithBS')
    )

    process.offlinePrimaryVertices = cms.EDProducer('RecoChargedRefCandidatePrimaryVertexSorter',
        assignment = cms.PSet(
            maxDistanceToJetAxis = cms.double(0.07),
            maxDtSigForPrimaryAssignment = cms.double(4.0),
            maxDxyForJetAxisAssigment = cms.double(0.1),
            maxDxyForNotReconstructedPrimary = cms.double(0.01),
            maxDxySigForNotReconstructedPrimary = cms.double(2),
            maxDzErrorForPrimaryAssignment = cms.double(0.05),
            maxDzForJetAxisAssigment = cms.double(0.1),
            maxDzForPrimaryAssignment = cms.double(0.1),
            maxDzSigForPrimaryAssignment = cms.double(5.0),
            maxJetDeltaR = cms.double(0.5),
            minJetPt = cms.double(25),
            preferHighRanked = cms.bool(False),
            useTiming = cms.bool(False)
        ),
        jets = cms.InputTag('ak4CaloJetsForTrk'),
        particles = cms.InputTag('trackRefsForJetsBeforeSorting'),
        produceAssociationToOriginalVertices = cms.bool(False),
        produceNoPileUpCollection = cms.bool(False),
        producePileUpCollection = cms.bool(False),
        produceSortedVertices = cms.bool(True),
        qualityForPrimary = cms.int32(3),
        sorting = cms.PSet(

        ),
        trackTimeResoTag = cms.InputTag(''),
        trackTimeTag = cms.InputTag(''),
        usePVMET = cms.bool(True),
        vertices = cms.InputTag('unsortedOfflinePrimaryVertices')
    )

    process.inclusiveVertexFinder = cms.EDProducer('InclusiveVertexFinder',
        beamSpot = cms.InputTag('offlineBeamSpot'),
        clusterizer = cms.PSet(
            clusterMaxDistance = cms.double(0.05),
            clusterMaxSignificance = cms.double(4.5),
            clusterMinAngleCosine = cms.double(0.5),
            distanceRatio = cms.double(20),
            maxTimeSignificance = cms.double(3.5),
            seedMax3DIPSignificance = cms.double(9999),
            seedMax3DIPValue = cms.double(9999),
            seedMin3DIPSignificance = cms.double(1.2),
            seedMin3DIPValue = cms.double(0.005)
        ),
        fitterRatio = cms.double(0.25),
        fitterSigmacut = cms.double(3),
        fitterTini = cms.double(256),
        maxNTracks = cms.uint32(30),
        maximumLongitudinalImpactParameter = cms.double(0.3),
        maximumTimeSignificance = cms.double(3),
        minHits = cms.uint32(8),
        minPt = cms.double(0.9),
        primaryVertices = cms.InputTag('offlinePrimaryVertices'),
        tracks = cms.InputTag('generalTracks'),
        useDirectVertexFitter = cms.bool(True),
        useVertexReco = cms.bool(True),
        vertexMinAngleCosine = cms.double(0.95),
        vertexMinDLen2DSig = cms.double(2.5),
        vertexMinDLenSig = cms.double(0.5),
        vertexReco = cms.PSet(
            finder = cms.string('avr'),
            primcut = cms.double(1),
            seccut = cms.double(3),
            smoothing = cms.bool(True)
        )
    )

    process.vertexMerger = cms.EDProducer('VertexMerger',
        maxFraction = cms.double(0.7),
        minSignificance = cms.double(2),
        secondaryVertices = cms.InputTag('inclusiveVertexFinder')
    )

    process.trackVertexArbitrator = cms.EDProducer('TrackVertexArbitrator',
        beamSpot = cms.InputTag('offlineBeamSpot'),
        dLenFraction = cms.double(0.333),
        dRCut = cms.double(0.4),
        distCut = cms.double(0.04),
        fitterRatio = cms.double(0.25),
        fitterSigmacut = cms.double(3),
        fitterTini = cms.double(256),
        maxTimeSignificance = cms.double(3.5),
        primaryVertices = cms.InputTag('offlinePrimaryVertices'),
        secondaryVertices = cms.InputTag('vertexMerger'),
        sigCut = cms.double(5),
        trackMinLayers = cms.int32(4),
        trackMinPixels = cms.int32(1),
        trackMinPt = cms.double(0.9),
        tracks = cms.InputTag('generalTracks')
    )

    process.inclusiveSecondaryVertices = cms.EDProducer('VertexMerger',
        maxFraction = cms.double(0.2),
        minSignificance = cms.double(10.0),
        secondaryVertices = cms.InputTag('trackVertexArbitrator')
    )

    process.initialStepTracksSelectionHighPurity = cms.EDProducer( "TrackCollectionFilterCloner",
        minQuality = cms.string( "highPurity" ),
        copyExtras = cms.untracked.bool( True ),
        copyTrajectories = cms.untracked.bool( False ),
        originalSource = cms.InputTag( "initialStepTracks" ),
        originalQualVals = cms.InputTag('initialStepTrackCutClassifier','QualityMasks' ),
        originalMVAVals = cms.InputTag('initialStepTrackCutClassifier','MVAValues' )
    )


    process.initialStepTrackCutClassifier = cms.EDProducer('TrackCutClassifier',
        beamspot = cms.InputTag('offlineBeamSpot'),
        ignoreVertices = cms.bool(False),
        mva = cms.PSet(
            dr_par = cms.PSet(
                d0err = cms.vdouble(0.003, 0.003, 0.003),
                d0err_par = cms.vdouble(0.001, 0.001, 0.001),
                dr_exp = cms.vint32(4, 4, 4),
                dr_par1 = cms.vdouble(0.8, 0.7, 0.6),
                dr_par2 = cms.vdouble(0.6, 0.5, 0.45)
            ),
            dz_par = cms.PSet(
                dz_exp = cms.vint32(4, 4, 4),
                dz_par1 = cms.vdouble(0.9, 0.8, 0.7),
                dz_par2 = cms.vdouble(0.8, 0.7, 0.55)
            ),
            maxChi2 = cms.vdouble(9999.0, 25.0, 16.0),
            maxChi2n = cms.vdouble(2.0, 1.4, 1.2),
            maxDr = cms.vdouble(0.5, 0.03, 3.40282346639e+38),
            maxDz = cms.vdouble(0.5, 0.2, 3.40282346639e+38),
            maxDzWrtBS = cms.vdouble(3.40282346639e+38, 24.0, 15.0),
            maxLostLayers = cms.vint32(3, 2, 2),
            min3DLayers = cms.vint32(3, 3, 3),
            minLayers = cms.vint32(3, 3, 3),
            minNVtxTrk = cms.int32(3),
            minNdof = cms.vdouble(1e-05, 1e-05, 1e-05),
            minPixelHits = cms.vint32(0, 0, 3)
        ),
        qualityCuts = cms.vdouble(-0.7, 0.1, 0.7),
        src = cms.InputTag('initialStepTracks'),
        vertices = cms.InputTag('pixelVertices')
    )

    process.initialStepTracksSelectionHighPurity = cms.EDProducer('TrackCollectionFilterCloner',
        copyExtras = cms.untracked.bool(True),
        copyTrajectories = cms.untracked.bool(False),
        minQuality = cms.string("highPurity"),
        originalMVAVals = cms.InputTag('initialStepTrackCutClassifier','MVAValues'),
        originalQualVals = cms.InputTag('initialStepTrackCutClassifier','QualityMasks'),
        originalSource = cms.InputTag('initialStepTracks','','RECO2')
    )


    ##StarUp
    process.itLocalReco = cms.Sequence(
        process.siPhase2Clusters
      + process.siPixelClusters
      + process.siPixelClusterShapeCache
      + process.siPixelRecHits
    )

    process.otLocalReco = cms.Sequence(
        process.MeasurementTrackerEvent
    )

    process.startUp = cms.Sequence(
        process.itLocalReco
        + process.offlineBeamSpot
        + process.otLocalReco
        + process.trackerClusterCheck
    )

    return process

def customise_hltPhase2_TRKv06(process):

    process = customise_common(process)

    process.caloTowerForTrk = cms.EDProducer('CaloTowersCreator',
        AllowMissingInputs = cms.bool(False),
        EBGrid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        EBSumThreshold = cms.double(0.2),
        EBThreshold = cms.double(0.07),
        EBWeight = cms.double(1.0),
        EBWeights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        EEGrid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        EESumThreshold = cms.double(0.45),
        EEThreshold = cms.double(0.3),
        EEWeight = cms.double(1.0),
        EEWeights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        EcalRecHitSeveritiesToBeExcluded = cms.vstring(
            'kTime',
            'kWeird',
            'kBad'
        ),
        EcalSeveritiesToBeUsedInBadTowers = cms.vstring(),
        EcutTower = cms.double(-1000.0),
        HBGrid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        HBThreshold = cms.double(1.2),
        HBThreshold1 = cms.double(0.8),
        HBThreshold2 = cms.double(1.2),
        HBWeight = cms.double(1.0),
        HBWeights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        HEDGrid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        HEDThreshold = cms.double(0.2),
        HEDThreshold1 = cms.double(0.1),
        HEDWeight = cms.double(1.0),
        HEDWeights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        HESGrid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        HESThreshold = cms.double(0.2),
        HESThreshold1 = cms.double(0.1),
        HESWeight = cms.double(1.0),
        HESWeights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        HF1Grid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        HF1Threshold = cms.double(0.5),
        HF1Weight = cms.double(1.0),
        HF1Weights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        HF2Grid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        HF2Threshold = cms.double(0.85),
        HF2Weight = cms.double(1.0),
        HF2Weights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        HOGrid = cms.vdouble(-1.0, 1.0, 10.0, 100.0, 1000.0),
        HOThreshold0 = cms.double(1.1),
        HOThresholdMinus1 = cms.double(3.5),
        HOThresholdMinus2 = cms.double(3.5),
        HOThresholdPlus1 = cms.double(3.5),
        HOThresholdPlus2 = cms.double(3.5),
        HOWeight = cms.double(1.0),
        HOWeights = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0),
        HcalAcceptSeverityLevel = cms.uint32(9),
        HcalAcceptSeverityLevelForRejectedHit = cms.uint32(9999),
        HcalPhase = cms.int32(1),
        HcalThreshold = cms.double(-1000.0),
        MomConstrMethod = cms.int32(1),
        MomEBDepth = cms.double(0.3),
        MomEEDepth = cms.double(0.0),
        MomHBDepth = cms.double(0.2),
        MomHEDepth = cms.double(0.4),
        UseEcalRecoveredHits = cms.bool(False),
        UseEtEBTreshold = cms.bool(False),
        UseEtEETreshold = cms.bool(False),
        UseHO = cms.bool(True),
        UseHcalRecoveredHits = cms.bool(True),
        UseRejectedHitsOnly = cms.bool(False),
        UseRejectedRecoveredEcalHits = cms.bool(False),
        UseRejectedRecoveredHcalHits = cms.bool(True),
        UseSymEBTreshold = cms.bool(True),
        UseSymEETreshold = cms.bool(True),
        ecalInputs = cms.VInputTag(cms.InputTag('ecalRecHit','EcalRecHitsEB'), cms.InputTag('ecalRecHit','EcalRecHitsEE')),
        hbheInput = cms.InputTag('hbhereco'),
        hfInput = cms.InputTag('hfreco'),
        hoInput = cms.InputTag('horeco'),
        missingHcalRescaleFactorForEcal = cms.double(0)
    )

    ## Seeding for Initial Step
    process.initialStepSeeds = cms.EDProducer('SeedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer',
        MinOneOverPtError = cms.double(1),
        OriginTransverseErrorMultiplier = cms.double(1),
        SeedComparitorPSet = cms.PSet(
            ClusterShapeCacheSrc = cms.InputTag('siPixelClusterShapeCache'),
            ClusterShapeHitFilterName = cms.string('ClusterShapeHitFilter'),
            ComponentName = cms.string('PixelClusterShapeSeedComparitor'),
            FilterAtHelixStage = cms.bool(False),
            FilterPixelHits = cms.bool(True),
            FilterStripHits = cms.bool(False)
        ),
        SeedMomentumForBOFF = cms.double(5),
        TTRHBuilder = cms.string('WithTrackAngle'),
        forceKinematicWithRegionDirection = cms.bool(False),
        magneticField = cms.string(''),
        propagator = cms.string('PropagatorWithMaterial'),
        seedingHitSets = cms.InputTag('initialStepHitQuadruplets')
    )

    process.initialStepHitDoublets = cms.EDProducer('HitPairEDProducer',
        clusterCheck = cms.InputTag('trackerClusterCheck'),
        layerPairs = cms.vuint32(0, 1, 2),
        maxElement = cms.uint32(50000000),
        maxElementTotal = cms.uint32(50000000),
        mightGet = cms.optional.untracked.vstring,
        produceIntermediateHitDoublets = cms.bool(True),
        produceSeedingHitSets = cms.bool(False),
        seedingLayers = cms.InputTag('initialStepSeedLayers'),
        trackingRegions = cms.InputTag('initialStepTrackingRegions'),
        trackingRegionsSeedingLayers = cms.InputTag('')
    )

    process.initialStepHitQuadruplets = cms.EDProducer('CAHitQuadrupletEDProducer',
        CAHardPtCut = cms.double(0),
        CAOnlyOneLastHitPerLayerFilter = cms.optional.bool,
        CAPhiCut = cms.double(0.175),
        CAThetaCut = cms.double(0.001),
        SeedComparitorPSet = cms.PSet(
            ComponentName = cms.string('LowPtClusterShapeSeedComparitor'),
            clusterShapeCacheSrc = cms.InputTag('siPixelClusterShapeCache'),
            clusterShapeHitFilter = cms.string('ClusterShapeHitFilter')
        ),
        doublets = cms.InputTag('initialStepHitDoublets'),
        extraHitRPhitolerance = cms.double(0.032),
        fitFastCircle = cms.bool(True),
        fitFastCircleChi2Cut = cms.bool(True),
        maxChi2 = cms.PSet(
            enabled = cms.bool(True),
            pt1 = cms.double(0.7),
            pt2 = cms.double(2),
            value1 = cms.double(200),
            value2 = cms.double(50)
        ),
        useBendingCorrection = cms.bool(True)
    )


    process.pixelTracksSequence = cms.Sequence(
        process.pixelTrackFilterByKinematics
      + process.pixelFitterByHelixProjections
      + process.pixelTracksTrackingRegions
      + process.pixelTracksSeedLayers
      + process.pixelTracksHitDoublets
      + process.pixelTracksHitQuadruplets
      + process.pixelTracks
    )

    process.pixelVerticesSequence = cms.Sequence(
        process.pixelVertices
    )

    process.initialStepSequence = cms.Sequence(
        process.initialStepSeedLayers
      + process.initialStepTrackingRegions
      + process.initialStepHitDoublets
      + process.initialStepHitQuadruplets
      + process.initialStepSeeds
      + process.initialStepTrackCandidates
      + process.initialStepTracks
      + process.initialStepTrackCutClassifier
      + process.initialStepTracksSelectionHighPurity
    )

    process.highPtTripletStepSequence = cms.Sequence(
        process.highPtTripletStepClusters
      + process.highPtTripletStepSeedLayers
      + process.highPtTripletStepTrackingRegions
      + process.highPtTripletStepHitDoublets
      + process.highPtTripletStepHitTriplets
      + process.highPtTripletStepSeeds
      + process.highPtTripletStepTrackCandidates
      + process.highPtTripletStepTracks
      + process.highPtTripletStepTrackCutClassifier
      + process.highPtTripletStepTracksSelectionHighPurity
    )

    process.vertexReco = cms.Sequence(
        process.firstStepPrimaryVerticesUnsorted
      + process.initialStepTrackRefsForJets
      + process.caloTowerForTrk
      + process.ak4CaloJetsForTrk
      + process.firstStepPrimaryVertices
      + process.trackTimeValueMapProducer
      + process.unsortedOfflinePrimaryVertices
      + process.trackWithVertexRefSelectorBeforeSorting
      + process.trackRefsForJetsBeforeSorting
      + process.offlinePrimaryVertices
      + process.offlinePrimaryVerticesWithBS
      + process.inclusiveVertexFinder
      + process.vertexMerger
      + process.trackVertexArbitrator
      + process.inclusiveSecondaryVertices
    )

    # ambiguities
    # process.globalreco_tracking
    if hasattr(process, 'globalreco_trackingTask'):
        del process.globalreco_trackingTask
    if hasattr(process,"trackTimeValueMapProducer"):
        del process.trackTimeValueMapProducer
    if hasattr(process,"gsfTrackTimeValueMapProducer"):
        del process.gsfTrackTimeValueMapProducer


    process.globalreco_tracking = cms.Path(
          process.startUp
        + process.pixelTracksSequence
        + process.pixelVerticesSequence
        + process.initialStepSequence
        + process.highPtTripletStepSequence
        + process.generalTracks
        + process.vertexReco
    )

    return process

def customise_hltPhase2_TRKv06_1(process):

    process = customise_common(process)

    # process.ak4CaloJetsForTrk.srcPVs = cms.InputTag("pixelVertices")

    process.seedFromProtoTracks = cms.PSet(
      TTRHBuilder = cms.string( "WithTrackAngle"), #hltESPTTRHBuilderPixelOnly" ),
      SeedMomentumForBOFF = cms.double( 5.0 ),
      propagator = cms.string( "PropagatorWithMaterial"),#" ), #
      forceKinematicWithRegionDirection = cms.bool( False ),
      magneticField = cms.string( ""), #" ),
      OriginTransverseErrorMultiplier = cms.double( 1.0 ),
      ComponentName = cms.string( "SeedFromConsecutiveHitsCreator" ),
      MinOneOverPtError = cms.double( 1.0 )
    )

    process.initialStepSeeds = cms.EDProducer( "SeedGeneratorFromProtoTracksEDProducer",
        useEventsWithNoVertex = cms.bool( True ),
        originHalfLength = cms.double(0.3),
        useProtoTrackKinematics = cms.bool( False ),
        usePV = cms.bool( False ),
        SeedCreatorPSet = cms.PSet(  refToPSet_ = cms.string( "seedFromProtoTracks" ) ),
        InputVertexCollection = cms.InputTag(""),
        TTRHBuilder = cms.string( "WithTrackAngle"), #hltESPTTRHBuilderPixelOnly" ),
        InputCollection = cms.InputTag( "pixelTracks" ),
        originRadius = cms.double( 0.1 )
    )




    process.pixelTracksSequence = cms.Sequence(
        process.pixelTrackFilterByKinematics +
        process.pixelFitterByHelixProjections +
        process.pixelTracksTrackingRegions +  # = hlt
        process.pixelTracksSeedLayers +
        process.pixelTracksHitDoublets +
        process.pixelTracksHitQuadruplets +
        process.pixelTracks
    )

    process.pixelVerticesSequence = cms.Sequence(
        process.pixelVertices
    )


    process.initialStepSequence = cms.Sequence(
        process.initialStepSeeds +
        process.initialStepTrackCandidates +
        process.initialStepTracks +
        process.initialStepTrackCutClassifier +
        process.initialStepTracksSelectionHighPurity
    )

    process.highPtTripletStepSequence = cms.Sequence(
        process.highPtTripletStepClusters +
        process.highPtTripletStepSeedLayers +
        process.highPtTripletStepTrackingRegions +
        process.highPtTripletStepHitDoublets +
        process.highPtTripletStepHitTriplets +
        process.highPtTripletStepSeeds +
        process.highPtTripletStepTrackCandidates +
        process.highPtTripletStepTracks +
        process.highPtTripletStepTrackCutClassifier +
        process.highPtTripletStepTracksSelectionHighPurity
    )



    process.vertexReco = cms.Sequence(
            process.firstStepPrimaryVerticesUnsorted
          + process.initialStepTrackRefsForJets
          + process.caloTowerForTrk
          + process.ak4CaloJetsForTrk
          + process.firstStepPrimaryVertices
          + process.trackTimeValueMapProducer
          + process.unsortedOfflinePrimaryVertices
          + process.trackWithVertexRefSelectorBeforeSorting
          + process.trackRefsForJetsBeforeSorting
          + process.offlinePrimaryVertices
          + process.offlinePrimaryVerticesWithBS
          + process.inclusiveVertexFinder
          + process.vertexMerger
          + process.trackVertexArbitrator
          + process.inclusiveSecondaryVertices
        )


    # ambiguities
    # process.globalreco_tracking

    if hasattr(process,"trackTimeValueMapProducer"):
        del process.trackTimeValueMapProducer
    if hasattr(process,"gsfTrackTimeValueMapProducer"):
        del process.gsfTrackTimeValueMapProducer


    process.tracking_v6_1 = cms.Sequence(
        process.startUp
      + process.pixelTracksSequence
      + process.pixelVerticesSequence
      + process.initialStepSequence
      + process.highPtTripletStepSequence
      + process.generalTracks
      + process.vertexReco
    )

    if hasattr(process, 'globalreco_trackingTask'):
        del process.globalreco_trackingTask

    process.reconstruction = cms.Sequence(process.tracking_v6_1)

    return process

def customizeOriginalTrimmingInitial(process,fraction=0.3,numVertex=20,minSumPt2=20):

        process.trimmedPixelVertices.fractionSumPt2 = cms.double(fraction)
        process.trimmedPixelVertices.maxVtx = cms.uint32(numVertex)
        process.trimmedPixelVertices.minSumPt2 = cms.double(minSumPt2)

        process.initialStepSeeds.usePV = cms.bool(False)
        process.initialStepSeeds.InputVertexCollection = cms.InputTag("trimmedPixelVertices")

        return process

def customizeOriginalTrimmingTriplet(process,fraction=0.3,numVertex=20,minSumPt2=20):

        process.trimmedPixelVertices.fractionSumPt2 = cms.double(fraction)
        process.trimmedPixelVertices.maxVtx = cms.uint32(numVertex)
        process.trimmedPixelVertices.minSumPt2 = cms.double(minSumPt2)

        process.highPtTripletStepTrackingRegions = process.trimmedVertexTrackingRegions.clone()

        return process

def customise_hltPhase2_TRKv07(process):

    process = customise_common(process)

    process.trimmedVertexTrackingRegions = cms.EDProducer( "GlobalTrackingRegionWithVerticesEDProducer",
        RegionPSet = cms.PSet(
          useFixedError = cms.bool( True ),
          nSigmaZ = cms.double( 4.0 ),
          VertexCollection = cms.InputTag( "trimmedPixelVertices" ), # trimmedPixelVertices
          beamSpot = cms.InputTag( "offlineBeamSpot" ),
          useFoundVertices = cms.bool( True ),
          fixedError = cms.double( 0.2 ),
          sigmaZVertex = cms.double( 3.0 ),
          useFakeVertices = cms.bool( False ),
          ptMin = cms.double( 0.9 ), # previous 0.4
          originRadius = cms.double( 0.02 ), # previous 0.05
          precise = cms.bool( True ),
          useMultipleScattering = cms.bool( False )
        ),
        mightGet = cms.optional.untracked.vstring  # cmssw_11_1
    )

    process.trimmedPixelVertices = cms.EDProducer( "PixelVertexCollectionTrimmer",
        src = cms.InputTag( "pixelVertices" ),
        fractionSumPt2 = cms.double( 0.00000001 ),
        minSumPt2 = cms.double( -100.0 ),
        PVcomparer = cms.PSet(  refToPSet_ = cms.string( "pSetPvClusterComparerForIT" ) ),
        maxVtx = cms.uint32( 0 ) # > 200 # previous 100
    )

    process.seedFromProtoTracks = cms.PSet(
      TTRHBuilder = cms.string( "WithTrackAngle"), #hltESPTTRHBuilderPixelOnly" ),
      SeedMomentumForBOFF = cms.double( 5.0 ),
      propagator = cms.string( "PropagatorWithMaterial"),#" ), #
      forceKinematicWithRegionDirection = cms.bool( False ),
      magneticField = cms.string( ""), #" ),
      OriginTransverseErrorMultiplier = cms.double( 1.0 ),
      ComponentName = cms.string( "SeedFromConsecutiveHitsCreator" ),
      MinOneOverPtError = cms.double( 1.0 )
    )

    process.initialStepSeeds = cms.EDProducer( "SeedGeneratorFromProtoTracksEDProducer",
        useEventsWithNoVertex = cms.bool( True ),
        originHalfLength = cms.double(0.3),
        useProtoTrackKinematics = cms.bool( False ),
        usePV = cms.bool( False ),
        SeedCreatorPSet = cms.PSet(  refToPSet_ = cms.string( "seedFromProtoTracks" ) ),
        InputVertexCollection = cms.InputTag(""),
        TTRHBuilder = cms.string( "WithTrackAngle"), #hltESPTTRHBuilderPixelOnly" ),
        InputCollection = cms.InputTag( "pixelTracks" ),
        originRadius = cms.double( 0.1 )
    )



    process = customizeOriginalTrimmingInitial(process)
    process = customizeOriginalTrimmingTriplet(process)

    process.pixelTracksSequence = cms.Sequence(
        process.pixelTrackFilterByKinematics +
        process.pixelFitterByHelixProjections +
        process.pixelTracksTrackingRegions +  # = hlt
        process.pixelTracksSeedLayers +
        process.pixelTracksHitDoublets +
        process.pixelTracksHitQuadruplets
    )

    process.pixelVerticesSequence = cms.Sequence(
        process.pixelVertices +
        process.trimmedPixelVertices
    )


    process.initialStepSequence = cms.Sequence(
        process.initialStepSeeds +
        process.initialStepTrackCandidates +
        process.initialStepTracks +
        process.initialStepTrackCutClassifier +
        process.initialStepTracksSelectionHighPurity
    )

    process.highPtTripletStepSequence = cms.Sequence(
        process.highPtTripletStepClusters +
        process.highPtTripletStepSeedLayers +
        process.highPtTripletStepTrackingRegions +
        process.highPtTripletStepHitDoublets +
        process.highPtTripletStepHitTriplets +
        process.highPtTripletStepSeeds +
        process.highPtTripletStepTrackCandidates +
        process.highPtTripletStepTracks +
        process.highPtTripletStepTrackCutClassifier +
        process.highPtTripletStepTracksSelectionHighPurity
    )



    process.vertexReco = cms.Sequence(
            process.ak4CaloJetsForTrk
          + process.unsortedOfflinePrimaryVertices
          + process.trackWithVertexRefSelectorBeforeSorting
          + process.trackRefsForJetsBeforeSorting
          + process.offlinePrimaryVertices
          + process.offlinePrimaryVerticesWithBS
          + process.inclusiveVertexFinder
          + process.vertexMerger
          + process.trackVertexArbitrator
          + process.inclusiveSecondaryVertices
        )


    # ambiguities
    # process.globalreco_tracking

    if hasattr(process,"trackTimeValueMapProducer"):
        del process.trackTimeValueMapProducer
    if hasattr(process,"gsfTrackTimeValueMapProducer"):
        del process.gsfTrackTimeValueMapProducer


    process.tracking_v6_1 = cms.Sequence(
        process.startUp
      + process.pixelTracksSequence
      + process.pixelVerticesSequence
      + process.initialStepSequence
      + process.highPtTripletStepSequence
      + process.generalTracks
      + process.vertexReco
    )

    if hasattr(process, 'globalreco_trackingTask'):
        del process.globalreco_trackingTask

    process.globalreco_tracking = cms.Sequence(process.tracking_v6_1)

    return process

# def customise_globalReco_hltPhase2_TRKv06_1(process):
#
#     process = customise_hltPhase2_TRKv06_1(process)
#
#
#
#     return process
#
